#from maintenance_loader import *

import imp, json, os, sys, hashlib, time, shutil, re, pathlib
import argparse, traceback
import csv, subprocess
from datetime import datetime, timedelta

def helpinfo():
    print ("")

parser = argparse.ArgumentParser("discord_exporter.py", add_help=False)
parser.add_argument('--help', '-h', action='count', help='get help')

parser.add_argument('--verbose', '-v', action='count', help='get output')
parser.add_argument('--servid', action='append', help='--servid <csvseparatedids>')
parser.add_argument('--outfolder', action='append', help='--outfolder <pathtofolder>')
parser.add_argument('--attachfolder', action='append', help='--attachfolder <pathtofolder>')
parser.add_argument('--conffile', action='append', help='--conffile <pathtofile>')
parser.add_argument('--chanid', action='append', help='--chanid <csvseparatedids>')
parser.add_argument('--noscan', action='store_true', help='')
parser.add_argument('--scanall', action='store_true', help='')
parser.add_argument('--nocompile', action='store_true', help='')

parser.add_argument('--compileonly', action='store_true', help='')
parser.add_argument('--allattach', action='store_true', help='')


SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))
#SCRIPTPATH = pathlib.Path(os.path.dirname(os.path.realpath(sys.argv[0])))
discordconf = imp.load_source('discordconf', os.path.join(SCRIPTPATH,'local_config','discordconf.py'))
discordcompile = imp.load_source('discordcompile', os.path.join(SCRIPTPATH,'python_libs','discord','compilediscord.py'))
driveutils = imp.load_source('driveutils', os.path.join(SCRIPTPATH,'python_libs','utils','log_utils.py'))
args = parser.parse_args()

runopts={}
if args.help is not None:
    helpinfo()
    parser.print_help()
    sys.exit(0)
varsargs=vars(args)
for i in varsargs:
    if varsargs[i] is not None:
        if isinstance(varsargs[i], list):
            runopts[i]=[]
            for j in varsargs[i]:
                runopts[i].append(j)
        elif varsargs[i] is not None:
            if varsargs[i] == True or varsargs[i] == False:
                runopts[i] = varsargs[i]
            else:
                runopts[i] = [varsargs[i]]

for i in runopts:
    if i == "servid":
        tmparr=[]
        for j in runopts[i]:
            tmparr.extend(j.split(","))
        runopts[i]=tmparr
if 'verbose' not in runopts.keys():
    runopts['verbose']=0


if not 'outfolder' in runopts.keys():
    outfolder=discordconf._DISCORDBACKUPS
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    runopts['outfolder']=[outfolder]
if not 'attachfolder' in runopts.keys():
    attachfolder=discordconf._DISCORDATTACHBACKUPS
    if not os.path.exists(attachfolder):
        os.makedirs(attachfolder)
    runopts['attachfolder']=[attachfolder]
if not 'tmpfolder' in runopts.keys():
    tmpfolder=discordconf._DISCORDTMPFOLDER
    if not os.path.exists(tmpfolder):
        os.makedirs(tmpfolder)
    runopts['tmpfolder']=[tmpfolder]
if not 'conffile' in runopts.keys():
    dlfile=driveutils.buildPath(SCRIPTPATH,'config','discord_channel_list.txt')
    if os.path.exists(dlfile):
        runopts['conffile']=[dlfile]

print(runopts)


timestr = time.strftime("%Y%m%d_%H%M%S")





def readDiscordChannelLog(logfile,type="greasemonkey"):
    IMPORTOBJ={}

    with open(logfile,'r',encoding="utf8") as f:
        for rline in f.readlines():
            if rline.count(',') < 4:
                continue
            pieces=rline.split(',')
            if pieces[0] not in IMPORTOBJ.keys():
                IMPORTOBJ[pieces[0]]=[]
            if type=="greasemonkey" or type=="configlog":
                obj={}
                if pieces[0]=="privatemsg":
                    obj['server']="Private Messages"
                    obj['serverid']="_privatemessages"
                    obj['role']=pieces[0].rstrip()
                    obj['user']=pieces[1].rstrip()
                    obj['task']=pieces[2].rstrip()
                    obj['id']=re.findall("^.*/\@me\/(\d+)\s*$",pieces[3])[0]
                    obj['name']=pieces[4].rstrip()
                    IMPORTOBJ[pieces[0]].append(obj)
                if pieces[0]=="servername" or pieces[0]=="serverchannel":
                    reg="^.*\/channels\/\d+\/(\d+)\s*$"
                    if pieces[0]=="servername":
                        reg="^.*\/channels\/(\d+)(?:\/\d*)?\s*"
                    if pieces[0]=="serverchannel" and 'servername' in IMPORTOBJ.keys():
                        serverid=re.findall("^.*\/channels\/(\d+)\/\d+\s*$",pieces[3])[0]
                        obj['serverid']=serverid
                        for servobj in IMPORTOBJ['servername']:
                            if servobj['id']==serverid:
                                obj['server']=servobj['name']
                    obj['role']=pieces[0].rstrip()
                    obj['user']=pieces[1].rstrip()
                    obj['task']=pieces[2].rstrip()
                    obj['id']=re.findall(reg,pieces[3])[0]
                    obj['name']=pieces[4].rstrip()
                    IMPORTOBJ[pieces[0]].append(obj)
    f.close()

    return IMPORTOBJ

def forceSafeFilename(filename):
    return re.sub('[^\w\-_\. ]', '_', filename)

def fetchDiscordList(channelid,tokenuserset):
    proccommand=[]
    proccommand.append(discordconf.EXPORTER_FULLPATH)
    if channelid == "_privatemessages":
        proccommand.append("dm")
    elif channelid == "_guildlist":
        proccommand.append("guilds")
    else:
        proccommand.append("channels")
        proccommand.append("--guild")
        proccommand.append(channelid)
    proccommand.append("--token")
    proccommand.append(tokenuserset['token'])

    proc = subprocess.Popen(proccommand, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    if err is None:
        targetlist={}
        linelist = (out.decode("utf-8")).split("\r\n")
        for line in linelist:
            if re.match(r"^\d+\s*\|\s*.*",line):
                id = re.findall(r"^(\d+)\s*\|\s*.*",line).pop()
                username = re.findall(r"^\d+\s*\|\s*(.*)",line).pop()
                targetlist[id]=username
        return targetlist
    else:
        print ("-----------------------------")
        print ("program err:")
        print (err)
        print ("-----------------------------")
        sys.exit(1)

def buildTargetList():
    targetlist={}
    for username,tokenuserset in discordconf.IMPORTDICT.items():
        if username not in targetlist.keys():
            targetlist[username]={}

        if discordcompile.filterDiscordIDs('privatemessages','servid',runopts):
            print ('fetch private message users')
            targetlist[username]['_privatemessages']=fetchDiscordList("_privatemessages",tokenuserset)
        print ('fetch server list')
        targetlist[username]['_guildlist']=fetchDiscordList("_guildlist",tokenuserset)
        print ('fetch server channel lists')
        targetlist[username]['_serverlist']={}
        for guildid,guildname in targetlist[username]['_guildlist'].items():
            if not discordcompile.filterDiscordIDs(guildid,'servid',runopts):
                continue
            print ('fetch server',guildname,guildid,'channel lists')
            targetlist[username]['_serverlist'][guildid]=fetchDiscordList(guildid,tokenuserset)

    return targetlist

def formatTargetList(targetlist):
    FormatList={}
    for username,listgroup in targetlist.items():
        if username not in FormatList.keys():
            FormatList[username]={}

        checktypes=['_privatemessages','_serverlist']
        if '_privatemessages' in listgroup.keys():
            if '_privatemessages' not in FormatList[username].keys():
                FormatList[username]['_privatemessages']={'channelist':{},'name':'Private Messages','safename':'Private Messages'}
                FormatList[username]['_privatemessages']['id']='_privatemessages'

            for targetid,targetname in listgroup['_privatemessages'].items():
                targetobj={'id':targetid,'name':targetname,'safename':forceSafeFilename(targetname)}
                FormatList[username]['_privatemessages']['channelist'][targetid]=targetobj

        if '_serverlist' in listgroup.keys() and '_guildlist' in listgroup.keys():
            for guildid,guildlist in listgroup['_serverlist'].items():
                #  Add guild information
                if guildid not in FormatList[username].keys():
                    FormatList[username][guildid]={'channelist':{}}
                    if guildid in listgroup['_guildlist'].keys():
                        FormatList[username][guildid]['name']=listgroup['_guildlist'][guildid]
                        FormatList[username][guildid]['safename']=forceSafeFilename(listgroup['_guildlist'][guildid])
                        FormatList[username][guildid]['id']=guildid

                for targetid,targetname in listgroup['_serverlist'][guildid].items():

                        targetobj={'id':targetid,'name':targetname,'safename':forceSafeFilename(targetname)}
                        FormatList[username][guildid]['channelist'][targetid]=targetobj
    return FormatList

def parseDiscordChannelLogList(channels,runopts):
    ScanList={}

    if 'noscan' in runopts.keys() and runopts['noscan'] == True:
        for type,list in channels.items():
            for item in list:
                username = item['user']
                if username not in ScanList.keys():
                    ScanList[username]={}

                if item['type'] == "privatemsg" and '_privatemessages' not in ScanList[username].keys():
                    ScanList[username]['_privatemessages'] = {}
                if item['type'] == "servername" and item['task'] == "addserver" and item['id'] not in ScanList[username].keys():
                    ScanList[username][item['id']] = {}
                if item['type'] == "serverchannel" and item['task'] == "addchannel" and item['serverid'] not in ScanList[username][username].keys():
                    ScanList[username][item['serverid']] = {}
                if item['task'] == "addchannel":
                    serverid = item['serverid']
                    if 'channelist' not in ScanList[username][serverid].keys():
                        ScanList[username][serverid]['channelist']={}
                    safename=forceSafeFilename(item['name'])
                    ScanList[username][serverid]['channelist'][item['id']]={'name':item['name'],'id':item['id'],'safename':safename}
                if item['type'] == "servername" and item['task'] == "addserver":
                    safename=forceSafeFilename(item['name'])
                    ScanList[username][item['id']]['name']=item['name']
                    ScanList[username][item['id']]['id']=item['id']
                    ScanList[username][item['id']]['safename']=safename
    else:
        targetlist = buildTargetList()
        ScanList = formatTargetList(targetlist)

    for type,list in channels.items():
        for item in list:
            if item['task'] == "removechannel":
                username = item['user']
                serverid = item['serverid']
                if item['id'] in ScanList[username][serverid]['channelist'].keys():
                    del ScanList[username][serverid]['channelist'][item['id']]
            if item['task'] == "removeserver":
                username = item['user']
                serverid = item['id']
                if serverid in ScanList[username].keys():
                    del ScanList[username][serverid]

    return ScanList

def getNewestSubtractDate(username,serverstr,channelid,runopts):
    if 'scanall' in runopts.keys() and runopts['scanall'] == True:
        return None
    datenotesfile = driveutils.buildPath(runopts['outfolder'][0],"discordtimelog","newest",username,serverstr,channelid+".txt")
    if not os.path.exists(datenotesfile):
        return None
    datestr=None
    for i, line in enumerate(open(datenotesfile,'r',encoding="utf8")):
        for match in re.finditer( re.compile("^(\d+-\d+-\d+)\s*"), line):
            datestr=match.groups()[0]
    if datestr is not None:
        date = datetime.strptime(datestr, '%Y-%m-%d')
        return date.strftime("%m-%d-%y")
#        d = date - timedelta(days=1)
#        return d.strftime("%m-%d-%y")

def saveScanDates(username,serverstr,channelid,outfolder,exportfile,runopts):
    datenotespathnew = driveutils.buildPath(outfolder,"discordtimelog","newest",username,serverstr)
    if not os.path.exists(datenotespathnew):
        os.makedirs(datenotespathnew)
    datenotespathold = driveutils.buildPath(outfolder,"discordtimelog","currentoldest",username,serverstr)
    if not os.path.exists(datenotespathold):
        os.makedirs(datenotespathold)

    oldestmatch=None
    newestmatch=None
    for i, line in enumerate(open(exportfile,'r',encoding="utf8")):
        for match in re.finditer( re.compile("chatlog__timestamp\">(\d+-\w+-\d+)\s+"), line):
            if oldestmatch is None:
                oldestmatch=match.groups()[0]
            newestmatch=match.groups()[0]
    if oldestmatch is None or newestmatch is None:
        return
#                    print 'Found on line %s: %s' % (i+1, match.groups())
    oldesttime = discordcompile.parseTimeObj(oldestmatch.split("-"))
    newesttime = discordcompile.parseTimeObj(newestmatch.split("-"))

    print ('save latest time:',newestmatch,',',datenotespathnew +channelid+'.txt')

    with open(driveutils.buildPath(datenotespathnew,channelid+'.txt'), 'w', encoding="utf8") as the_file:
        the_file.write(newesttime['year']+"-"+newesttime['month']+"-"+newesttime['day']+'\n')
    with open(driveutils.buildPath(datenotespathold,channelid+'.txt'), 'w', encoding="utf8") as the_file:
        the_file.write(oldesttime['year']+"-"+oldesttime['month']+"-"+oldesttime['day']+'\n')


def exportFromDiscord(username,servername,serverid,channelid,channelname,channelinfo,tmpoutfolder,timestr):
    dump=driveutils.buildPath("tmp","discord_dump.txt")
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    if os.path.isfile(dump):
        os.remove(dump)

    #################################################################### WORKING ON BUILDING TARGET LIST
    if username in discordconf.IMPORTDICT.keys():
        tokenuserset = discordconf.IMPORTDICT[username]
        if 'token' in tokenuserset.keys():
            serverstr=servername+"-"+serverid


            cmdstring=discordconf.EXPORTER_FULLPATH+" export --token \""+tokenuserset['token']+"\" --channel "+channelid

            subdate=getNewestSubtractDate(username,serverstr,channelid,runopts)
            if subdate is not None:
                cmdstring+=" --after "+subdate
            cmdstring+=" --output "+dump#+" >/dev/null"

#            os.system(cmdstring)
            subprocess.check_output(cmdstring, shell=True)

            folderpath = driveutils.buildPath(tmpoutfolder,"discordexport","tmp","exported",username,timestr,serverstr)
            if not os.path.exists(folderpath):
                os.makedirs(folderpath)

            if os.path.exists(dump):
                textfile = driveutils.buildPath(folderpath,channelname+"-"+channelid+".txt")
                shutil.copyfile(dump,textfile)
#                print('saved to: ', textfile)
            else:
                print (" * failed on: ",servername,channelid)


            if os.path.isfile(dump):
                os.remove(dump)





#if not 'loadfolder' in runopts.keys() and not 'loadfile' in runopts.keys():
#    if 'dlfolder' in arglist:
#        dlfolder=discordconf._HOME+"/Downloads"
#        if os.path.exists(dlfolder):
#            runopts['loadfolder']=dlfolder

if "compileonly" in runopts.keys() and runopts["compileonly"] == True:
    discordcompile.compileDiscordLogs(runopts['outfolder'][0],runopts['tmpfolder'][0],runopts)
    if "allattach" in runopts.keys():
        discordcompile.downloadAllAttachmentsDiscordLogs(runopts['outfolder'][0],runopts)
    sys.exit(0)




if "conffile" in runopts.keys() and os.path.exists(runopts["conffile"][0]):
    channels=readDiscordChannelLog(runopts["conffile"][0],"configlog")
    targetlist=parseDiscordChannelLogList(channels,runopts)
    discordcompile.clearTmpFolders( driveutils.buildPath(runopts['tmpfolder'][0],"discordexport","tmp","exported"), False )

    for username,itemlist in targetlist.items():
        if '_privatemessages' in itemlist.keys() and 'channelist' in itemlist['_privatemessages'].keys():
            for channelid,channelinfo in itemlist['_privatemessages']['channelist'].items():
                if not discordcompile.filterDiscordIDs(channelid,'chanid',runopts):
                    continue
                print ('export: _privatemessages',channelid)
                exportFromDiscord(username,"","privatemessages",channelinfo['id'],channelinfo['safename'],channelinfo,runopts['tmpfolder'][0],timestr)
        for serverid,serverobj in itemlist.items():
            servername = serverobj['name']
            if serverid != '_privatemessages' and servername != 'Private Messages' and 'channelist' in serverobj.keys():
                serversafename = serverobj['safename']
                for channelid,channelinfo in itemlist[serverid]['channelist'].items():
                    if not discordcompile.filterDiscordIDs(channelid,'chanid',runopts):
                        continue
                    print ('export: ',serversafename,channelid)
                    exportFromDiscord(username,serverid,serversafename,channelinfo['id'],channelinfo['safename'],channelinfo,runopts['tmpfolder'][0],timestr)

#sys.exit(0)
if "nocompile" not in runopts.keys():
    discordcompile.compileDiscordLogs(runopts['outfolder'][0],runopts['tmpfolder'][0],runopts)
if "allattach" in runopts.keys():
    discordcompile.downloadAllAttachmentsDiscordLogs(runopts['outfolder'][0],runopts)


if "conffile" in runopts.keys() and os.path.exists(runopts["conffile"][0]):
    channels=readDiscordChannelLog(runopts["conffile"][0],"configlog")
    targetlist=parseDiscordChannelLogList(channels,runopts)
    for username,itemlist in targetlist.items():
        for serverid,serverobj in itemlist.items():
            if not discordcompile.filterDiscordIDs(serverid,'servid',runopts):
                continue
            serverstr=serverid+"-"+serverobj['safename']
            for channelid,channelinfo in itemlist[serverid]['channelist'].items():
                if not discordcompile.filterDiscordIDs(channelid,'chanid',runopts):
                    continue
                folderpath = driveutils.buildPath(tmpfolder,"discordexport","tmp","exported",username,timestr,serverstr)
                textfile = driveutils.buildPath(folderpath,channelinfo['safename']+"-"+channelid+".txt")
                if os.path.exists(textfile):
                    saveScanDates(username,serverstr,channelid,runopts['outfolder'][0],textfile,runopts)

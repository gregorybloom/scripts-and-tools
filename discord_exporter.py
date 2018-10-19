#from maintenance_loader import *
import imp, os, sys, hashlib, time, shutil, re
import csv, subprocess
from datetime import datetime, timedelta

#   useconfs or compileonly


SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
discordconf = imp.load_source('discordconf', SCRIPTPATH+'/local_config/discordconf.py')
discordcompile = imp.load_source('discordcompile', SCRIPTPATH+'/python_libs/compile/compilediscord.py')
driveutils = imp.load_source('driveutils', SCRIPTPATH+'/python_libs/utils/log_utils.py')

def readDiscordChannelLog(logfile,type="greasemonkey"):
    IMPORTOBJ={}

    with open(logfile,'rb') as f:
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
        linelist = out.split("\r\n")
        for line in linelist:
            if re.match(r"^\d+\s*\|\s*.*",line):
                id = re.findall(r"^(\d+)\s*\|\s*.*",line).pop()
                username = re.findall(r"^\d+\s*\|\s*(.*)",line).pop()
                targetlist[id]=username
        return targetlist
    else:
        print "-----------------------------"
        print "program err:"
        print err
        print "-----------------------------"
        sys.exit(1)

def buildTargetList():
    targetlist={}
    for username,tokenuserset in discordconf.IMPORTDICT.iteritems():
        if username not in targetlist.keys():
            targetlist[username]={}

        print 'fetch private message users'
        targetlist[username]['_privatemessages']=fetchDiscordList("_privatemessages",tokenuserset)
        print 'fetch server list'
        targetlist[username]['_guildlist']=fetchDiscordList("_guildlist",tokenuserset)
        print 'fetch server channel lists'
        targetlist[username]['_serverlist']={}
        for guildid,guildname in targetlist[username]['_guildlist'].iteritems():
            print 'fetch server',guildname,guildid,'channel lists'
            targetlist[username]['_serverlist'][guildid]=fetchDiscordList(guildid,tokenuserset)

    return targetlist

def formatTargetList(targetlist):
    FormatList={}
    for username,listgroup in targetlist.iteritems():
        if username not in FormatList.keys():
            FormatList[username]={}

        checktypes=['_privatemessages','_serverlist']
        if '_privatemessages' in listgroup.keys():
            if '_privatemessages' not in FormatList[username].keys():
                FormatList[username]['_privatemessages']={'channelist':{},'name':'Private Messages','safename':'Private Messages'}
                FormatList[username]['_privatemessages']['id']='_privatemessages'

            for targetid,targetname in listgroup['_privatemessages'].iteritems():
                targetobj={'id':targetid,'name':targetname,'safename':forceSafeFilename(targetname)}
                FormatList[username]['_privatemessages']['channelist'][targetid]=targetobj

        if '_serverlist' in listgroup.keys() and '_guildlist' in listgroup.keys():
            for guildid,guildlist in listgroup['_serverlist'].iteritems():
                #  Add guild information
                if guildid not in FormatList[username].keys():
                    FormatList[username][guildid]={'channelist':{}}
                    if guildid in listgroup['_guildlist'].keys():
                        FormatList[username][guildid]['name']=listgroup['_guildlist'][guildid]
                        FormatList[username][guildid]['safename']=forceSafeFilename(listgroup['_guildlist'][guildid])
                        FormatList[username][guildid]['id']=guildid

                for targetid,targetname in listgroup['_serverlist'][guildid].iteritems():

                        targetobj={'id':targetid,'name':targetname,'safename':forceSafeFilename(targetname)}
                        FormatList[username][guildid]['channelist'][targetid]=targetobj
    return FormatList

def parseDiscordChannelLogList(channels,runopts):
    ScanList={}

    if 'noscan' in runopts.keys() and runopts['noscan'] == True:
        for type,list in channels.iteritems():
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

    for type,list in channels.iteritems():
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
    datenotesfile = runopts['outfolder']+"/discordtimelog/newest/"+username+"/"+serverstr+"/"+channelid+".txt"
    if not os.path.exists(datenotesfile):
        return None
    datestr=None
    for i, line in enumerate(open(datenotesfile)):
        for match in re.finditer( re.compile("^(\d+-\d+-\d+)\s*"), line):
            datestr=match.groups()[0]
    if datestr is not None:
        date = datetime.strptime(datestr, '%Y-%m-%d')
        return date.strftime("%m-%d-%y")
#        d = date - timedelta(days=1)
#        return d.strftime("%m-%d-%y")

def saveScanDates(username,serverstr,channelid,outfolder,exportfile,runopts):
    datenotespathnew = outfolder+"/discordtimelog/newest/"+username+"/"+serverstr+"/"
    if not os.path.exists(datenotespathnew):
        os.makedirs(datenotespathnew)
    datenotespathold = outfolder+"/discordtimelog/currentoldest/"+username+"/"+serverstr+"/"
    if not os.path.exists(datenotespathold):
        os.makedirs(datenotespathold)

    oldestmatch=None
    newestmatch=None
    for i, line in enumerate(open(exportfile)):
        for match in re.finditer( re.compile("chatlog__timestamp\">(\d+-\w+-\d+)\s+"), line):
            if oldestmatch is None:
                oldestmatch=match.groups()[0]
            newestmatch=match.groups()[0]
    if oldestmatch is None or newestmatch is None:
        return
#                    print 'Found on line %s: %s' % (i+1, match.groups())
    oldesttime = discordcompile.parseTimeObj(oldestmatch.split("-"))
    newesttime = discordcompile.parseTimeObj(newestmatch.split("-"))

    print 'save last time:',newestmatch,',',newesttime

    with open(datenotespathnew +channelid+'.txt', 'w') as the_file:
        the_file.write(newesttime['year']+"-"+newesttime['month']+"-"+newesttime['day']+'\n')
    with open(datenotespathold +channelid+'.txt', 'w') as the_file:
        the_file.write(oldesttime['year']+"-"+oldesttime['month']+"-"+oldesttime['day']+'\n')


def exportFromDiscord(username,servername,serverid,channelid,channelname,channelinfo,tmpoutfolder,timestr):
    dump="tmp/discord_dump.txt"
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
            cmdstring+=" --output "+dump+" >/dev/null"

            os.system(cmdstring)


            folderpath = tmpoutfolder+"/discordexport/tmp/exported/"+username+"/"+timestr+"/"+serverstr+"/"
            if not os.path.exists(folderpath):
                os.makedirs(folderpath)

            if os.path.exists(dump):
                textfile = folderpath+"/"+channelname+"-"+channelid+".txt"
                shutil.copyfile(dump,textfile)
            else:
                print " * failed on: ",servername,channelid



            if os.path.isfile(dump):
                os.remove(dump)



timestr = time.strftime("%Y%m%d_%H%M%S")

runopts={}

arglist=sys.argv[1:]
if "outfolder" in arglist:
	pt=arglist.index("outfolder")+1
	if pt < len(arglist):
		runopts['outfolder']=arglist[pt]
if "tmpfolder" in arglist:
	pt=arglist.index("tmpfolder")+1
	if pt < len(arglist):
		runopts['tmpfolder']=arglist[pt]
if "chanid" in arglist:
	pt=arglist.index("chanid")+1
	if pt < len(arglist):
		runopts['chanid']=arglist[pt]


#if not 'loadfolder' in runopts.keys() and not 'loadfile' in runopts.keys():
#    if 'dlfolder' in arglist:
#        dlfolder=discordconf._HOME+"/Downloads"
#        if os.path.exists(dlfolder):
#            runopts['loadfolder']=dlfolder

if not 'outfolder' in runopts.keys():
    outfolder=discordconf._DISCORDBACKUPS
    if os.path.exists(outfolder):
        runopts['outfolder']=outfolder
    else:
        os.makedirs(outfolder)
        runopts['outfolder']=outfolder
if not 'tmpfolder' in runopts.keys():
    tmpfolder=discordconf._DISCORDTMPFOLDER
    if os.path.exists(tmpfolder):
        runopts['tmpfolder']=tmpfolder
    else:
        os.makedirs(tmpfolder)
        runopts['tmpfolder']=tmpfolder

if "noscan" in arglist:
    runopts['noscan']=True
if "scanall" in arglist:
    runopts['scanall']=True
if "nocompile" in arglist:
    runopts['nocompile']=True
if "compileonly" in arglist:
    discordcompile.compileDiscordLogs(runopts['outfolder'],runopts['tmpfolder'],runopts)
    sys.exit(0)
if "useconfs" in arglist:
    dlfile=SCRIPTPATH+'/config/discord_channel_list.txt'
    if os.path.exists(dlfile):
        if 'conffile' not in runopts.keys():
            runopts['conffile']=dlfile



if "conffile" in runopts.keys() and os.path.exists(runopts["conffile"]):
    channels=readDiscordChannelLog(runopts["conffile"],"configlog")
    targetlist=parseDiscordChannelLogList(channels,runopts)
    discordcompile.clearTmpFolders( runopts['tmpfolder']+"/discordexport/tmp/exported/", False )

    for username,itemlist in targetlist.iteritems():
        if '_privatemessages' in itemlist.keys() and 'channelist' in itemlist['_privatemessages'].keys():
            for channelid,channelinfo in itemlist['_privatemessages']['channelist'].iteritems():
                print 'export: _privatemessages',channelid
                exportFromDiscord(username,"","privatemessages",channelinfo['id'],channelinfo['safename'],channelinfo,runopts['tmpfolder'],timestr)
        for serverid,serverobj in itemlist.iteritems():
            servername = serverobj['name']
            if serverid != '_privatemessages' and servername != 'Private Messages' and 'channelist' in serverobj.keys():
                serversafename = serverobj['safename']
                for channelid,channelinfo in itemlist[serverid]['channelist'].iteritems():
                    print 'export: ',serversafename,channelid
                    exportFromDiscord(username,serverid,serversafename,channelinfo['id'],channelinfo['safename'],channelinfo,runopts['tmpfolder'],timestr)


if "nocompile" not in runopts.keys():
    discordcompile.compileDiscordLogs(runopts['outfolder'],runopts['tmpfolder'],runopts)


if "conffile" in runopts.keys() and os.path.exists(runopts["conffile"]):
    channels=readDiscordChannelLog(runopts["conffile"],"configlog")
    targetlist=parseDiscordChannelLogList(channels,runopts)
    for username,itemlist in targetlist.iteritems():
        for serverid,serverobj in itemlist.iteritems():
            serverstr=serverid+"-"+serverobj['safename']
            for channelid,channelinfo in itemlist[serverid]['channelist'].iteritems():
                folderpath = tmpfolder+"/discordexport/tmp/exported/"+username+"/"+timestr+"/"+serverstr+"/"
                textfile = folderpath+"/"+channelinfo['safename']+"-"+channelid+".txt"
                if os.path.exists(textfile):
                    saveScanDates(username,serverstr,channelid,runopts['outfolder'],textfile,runopts)

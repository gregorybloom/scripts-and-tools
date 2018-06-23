#from maintenance_loader import *
import imp, os, sys, hashlib, time, shutil, re
import csv

#   useconfs or compileonly


SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
discordconf = imp.load_source('discordconf', SCRIPTPATH+'/local_config/discordconf.py')
discordcompile = imp.load_source('discordcompile', SCRIPTPATH+'/python_libs/compile/compilediscord.py')
driveutils = imp.load_source('driveutils', SCRIPTPATH+'/python_libs/utils/log_utils.py')

def readDiscordChannelLog(logfile,type="greasemonkey"):
    IMPORTOBJ={}
    with open(logfile,'rb') as f:
        for rline in f.readlines():
            if rline.count(',') < 3:
                continue
            pieces=rline.split(',')
            if pieces[0] not in IMPORTOBJ.keys():
                IMPORTOBJ[pieces[0]]=[]
            if type=="greasemonkey" or type=="configlog":
                obj={}
                if pieces[0]=="privatemsg":
                    obj['server']="Private Messages"
                    obj['user']=pieces[1].rstrip()
                    obj['id']=re.findall("^.*/\@me\/(\d+)\s*$",pieces[2])[0]
                    obj['name']=pieces[3].rstrip()
                    IMPORTOBJ[pieces[0]].append(obj)
                if pieces[0]=="servername" or pieces[0]=="serverchannel":
                    reg="^.*\/channels\/\d+\/(\d+)\s*$"
                    if pieces[0]=="servername":
                        reg="^.*\/channels\/(\d+)(?:\/\d*)?\s*"
                    if pieces[0]=="serverchannel" and 'servername' in IMPORTOBJ.keys():
                        serverid=re.findall("^.*\/channels\/(\d+)\/\d+\s*$",pieces[2])[0]
                        obj['serverid']=serverid
                        for servobj in IMPORTOBJ['servername']:
                            if servobj['id']==serverid:
                                obj['server']=servobj['name']
                    obj['user']=pieces[1].rstrip()
                    obj['id']=re.findall(reg,pieces[2])[0]
                    obj['name']=pieces[3].rstrip()
                    IMPORTOBJ[pieces[0]].append(obj)
    f.close()
    return IMPORTOBJ

def exportFromDiscord(logusername,channelid,channelname,channelinfo,outfolder,timestr):
    dump="tmp/discord_dump.txt"
    if os.path.isfile(dump):
        os.remove(dump)

    for username,tokenuserset in discordconf.IMPORTDICT.iteritems():
        if logusername == username:
            if 'token' in tokenuserset.keys():
                print "Export Discord: "+username,channelname,channelid

                cmdstring=discordconf.EXPORTER_FULLPATH+" --token \""+tokenuserset['token']+"\" --channel "+channelid+" --output "+dump
                os.system(cmdstring)

                servername="unknown"
                if 'server' in channelinfo.keys():
                    servername=channelinfo['server']
                    if 'serverid' in channelinfo.keys():
                        servername+=" ("+channelinfo['serverid']+")"
                elif 'serverid' in channelinfo.keys():
                    servername=channelinfo['serverid']

                folderpath = outfolder+"/discordexport/tmp/"+username+"/"+timestr+"/"+servername+"/"
                if not os.path.exists(folderpath):
                    os.makedirs(folderpath)
                textfile = folderpath+"/"+channelname+".txt"
                shutil.copyfile(dump,textfile)

                if os.path.isfile(dump):
                    os.remove(dump)



timestr = time.strftime("%Y%m%d_%H%M%S")

runopts={}

arglist=sys.argv[1:]
if "outfolder" in arglist:
	pt=arglist.index("outfolder")+1
	if pt < len(arglist):
		runopts['outfolder']=arglist[pt]
if "chanid" in arglist:
	pt=arglist.index("chanid")+1
	if pt < len(arglist):
		runopts['chanid']=arglist[pt]
if "loadfile" in arglist:
	pt=arglist.index("loadfile")+1
	if pt < len(arglist):
		runopts['loadfile']=arglist[pt]
if "loadfolder" in arglist:
	pt=arglist.index("loadfolder")+1
	if pt < len(arglist):
		runopts['loadfolder']=arglist[pt]

if not 'loadfolder' in runopts.keys() and not 'loadfile' in runopts.keys():
    if 'dlfolder' in arglist:
        dlfolder=discordconf._HOME+"/Downloads"
        if os.path.exists(dlfolder):
            runopts['loadfolder']=dlfolder

if not 'outfolder' in runopts.keys():
    outfolder=discordconf._DISCORDBACKUPS
    if os.path.exists(outfolder):
        runopts['outfolder']=outfolder
    else:
        os.makedirs(outfolder)
        runopts['outfolder']=outfolder


if "nocompile" in arglist:
    runopts['nocompile']=True
if "compileonly" in arglist:
    discordcompile.compileDiscordLogs(runopts['outfolder'],runopts)
    sys.exit()
if "useconfs" in arglist:
    dlfile=SCRIPTPATH+'/config/discord_channel_list.txt'
    if os.path.exists(dlfile):
        if 'conffile' not in runopts.keys():
            runopts['conffile']=dlfile


#if "chanid" in runopts.keys():
#    pieces=runopts["chanid"].split(',')
#    for id in pieces:
#        exportFromDiscord("_any",id,id,{},runopts['outfolder'],timestr)

if "loadfile" in runopts.keys() and os.path.exists(runopts["loadfile"]):
    channels=readDiscordChannelLog(runopts["loadfile"])
    if 'privatemsg' in channels.keys():
        for channelinfo in channels['privatemsg']:
            exportFromDiscord(channelinfo['user'],channelinfo['id'],channelinfo['name'],channelinfo,runopts['outfolder'],timestr)
if "conffile" in runopts.keys() and os.path.exists(runopts["conffile"]):
    channels=readDiscordChannelLog(runopts["conffile"],"configlog")
    if 'privatemsg' in channels.keys():
        for channelinfo in channels['privatemsg']:
            exportFromDiscord(channelinfo['user'],channelinfo['id'],channelinfo['name'],channelinfo,runopts['outfolder'],timestr)
    if 'serverchannel' in channels.keys():
        for channelinfo in channels['serverchannel']:
            exportFromDiscord(channelinfo['user'],channelinfo['id'],channelinfo['name'],channelinfo,runopts['outfolder'],timestr)

if "loadfolder" in runopts.keys() and os.path.exists(runopts["loadfolder"]):
    filelist = driveutils.readDir(runopts["loadfolder"])
    closematches=[]
    matchkeys={}
    for filename in filelist:
        if re.match("DiscordSummary[\d\(\)\s]*\.txt",filename):
            closematches.append(filename)
            keyid=-1
            if re.match("^DiscordSummary\.txt$",filename):
                keyid=0
            elif re.match("^DiscordSummary\s*\((\d+)\)\.txt$",filename):
                keyid=re.findall("^DiscordSummary\s*\((\d+)\)\.txt$",filename)[0]
            matchkeys[int(keyid)]=filename
    targetfile = None
    if len(closematches) == 0:
        sys.exit()
    if len(closematches) == 1:
        targetfile=closematches[0]
    else:
        targetnum=max(matchkeys.keys())
        targetfile=matchkeys[targetnum]

    if targetfile is not None:
        print "Opening: "+targetfile
        targetfile=runopts["loadfolder"]+"/"+targetfile
        channels=readDiscordChannelLog(targetfile)
        if 'privatemsg' in channels.keys():
            for channelinfo in channels['privatemsg']:
                exportFromDiscord(channelinfo['user'],channelinfo['id'],channelinfo['name'],channelinfo,runopts['outfolder'],timestr)



discordcompile.compileDiscordLogs(runopts['outfolder'],runopts)

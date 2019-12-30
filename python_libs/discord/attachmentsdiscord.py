import imp, os, sys, hashlib, time, shutil, re, pathlib, random
import csv, json
import filecmp
import urllib,ssl
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


_SUBSCRIPTPATH = os.path.join(*list(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parts[0:-2]))

driveutils = imp.load_source('driveutils', os.path.join(_SUBSCRIPTPATH,'python_libs','utils','log_utils.py'))

def buildAttachmentsFromTmp(overallfolderpath,tmpoutputfolder,username,servername,channelname,runopts):
    # downloads attachments from the tmp/segments/ architecture
    segmentspath=driveutils.buildPath(tmpoutputfolder,"tmp","segments",username,servername,channelname)
    discordlogs=driveutils.buildPath(overallfolderpath,"discordchatlogs",username,servername,channelname)

    if not os.path.exists(discordlogs):
        os.makedirs(discordlogs)

#    print('tmpattach1.',segmentspath)
    filelist = driveutils.readDir(segmentspath)
    filelist.sort()

    attachmentlogpath=driveutils.buildPath(overallfolderpath,"discordattachlog")
#    print('tmpattach2.',attachmentlogpath)
    for timefolder in filelist:
        folderpath = driveutils.buildPath(segmentspath,timefolder)
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):
            if not os.path.exists(folderpath):
                os.makedirs(folderpath)

#            d=re.findall("^(\d{4})(\d\d)(\d\d)\s*$",timefolder)[0]

#            print('tmpattach3.',folderpath)
            loglist = driveutils.readDir(folderpath)
            loglist.sort()

            for logitem in loglist:
                if runopts['verbose'] > 0:
                    print ('  .. ',username,servername,channelname,timefolder)
                logpath = driveutils.buildPath(segmentspath,timefolder,logitem)
                if os.path.isfile(logpath) and re.match("^\d{4}\.txt\s*$",logitem):
#                    print('tmpattach4.',logpath)
                    getAttachments(logpath,driveutils.buildPath(runopts['attachfolder'][0],"discordattachments"),"attachments",attachmentlogpath,runopts)
                    getAttachments(logpath,driveutils.buildPath(runopts['attachfolder'][0],"discordavatars"),"avatars",attachmentlogpath,runopts)
    saveAllAttachmentFailureLogs(attachmentlogpath,runopts)

def buildAllAttachments(overallfolderpath,username,servername,channelname,runopts):
    discordlogs=driveutils.buildPath(overallfolderpath,"discordchatlogs",username,servername,channelname)
    filelist = driveutils.readDir(discordlogs)
    filelist.sort()
    attachmentlogpath=driveutils.buildPath(overallfolderpath,"discordattachlog")
    for timefile in filelist:
        if os.path.isfile(driveutils.buildPath(discordlogs,timefile)) and re.match("^\d{4}_\d{2}_\d{2}\.html\s*$",timefile):
            if runopts['verbose'] > 0:
                print ('  .. ',username,servername,channelname,timefile)
            timefolder=re.sub("_","",timefile)
            timefolder=re.findall("^(\d+)",timefolder).pop()
            getAttachments(driveutils.buildPath(discordlogs,timefile),driveutils.buildPath(runopts['attachfolder'][0],"discordattachments"),"attachments",attachmentlogpath,runopts)
            getAttachments(driveutils.buildPath(discordlogs,timefile),driveutils.buildPath(runopts['attachfolder'][0],"discordavatars"),"avatars",attachmentlogpath,runopts)
    saveAllAttachmentFailureLogs(attachmentlogpath,runopts)

def loadAttachmentLog(logfolder):
    logarray={}
    logarray['attachments']=[]
    logarray['avatars']=[]

    setarray=['attachments','avatars']
    for item in setarray:
        logfile = item+".txt"
        attachlogfile=driveutils.buildPath(logfolder,logfile)
        if not os.path.exists(attachlogfile):
            driveutils.createNewLog(attachlogfile,True)
        with open(attachlogfile,'r',encoding="utf8") as f:
            for rline in f.readlines():
                matchreg="https\:\/\/cdn\.discordapp\.com\/"
                if re.match(matchreg,rline):
                    logarray[item].append(rline.rstrip())
    return logarray

def loadAttachmentFailureLog(logfolder):
    logarray={}
    logarray['attachments']={}
    logarray['avatars']={}

    setarray=['attachments','avatars']
    for item in setarray:
        logfile = item+".fails.txt"
        attachlogfile=driveutils.buildPath(logfolder,logfile)
        if not os.path.exists(attachlogfile):
            driveutils.createNewLog(attachlogfile,True)
        with open(attachlogfile,'r',encoding="utf8") as f:
            for rline in f.readlines():
                matchreg=".*https\:\/\/cdn\.discordapp\.com\/.*"
                if re.match(matchreg,rline):
                    urltxt=re.findall("^.*\},(https\:\/\/\S+)",rline.rstrip()).pop()
                    obj={'url':urltxt,'errs':{}}
                    obj['errs']=json.loads(re.findall("^\s*(\{.*\}),https\:\/\/",rline.rstrip()).pop())['errs']
                    logarray[item][urltxt] = obj
    return logarray


def addAttachmentFailureLog(url,dltype,logfolder,exception,runopts):

    if url not in runopts['attachfailurelog'][dltype].keys():
        runopts['attachfailurelog'][dltype][url]={'url':url,'errs':{}}
    if exception not in runopts['attachfailurelog'][dltype][url]['errs'].keys():
        runopts['attachfailurelog'][dltype][url]['errs'][exception]=0
    runopts['attachfailurelog'][dltype][url]['errs'][exception]+=1

    if dltype not in runopts['attachfailurechecklog'].keys():
        runopts['attachfailurechecklog'][dltype]={}
    if url not in runopts['attachfailurechecklog'][dltype].keys():
        runopts['attachfailurechecklog'][dltype][url]={'errs':{}}
    runopts['attachfailurechecklog'][dltype][url]['errs'][exception]=True

def saveAllAttachmentFailureLogs(logfolder,runopts):
    for dltype in runopts['attachfailurelog'].keys():
        logfile=driveutils.buildPath(logfolder,dltype+".fails.txt")
        driveutils.createNewLog(logfile+".1",False)
        attachmentfile = open(logfile+".1", 'a', encoding="utf8")
        for url in runopts['attachfailurelog'][dltype].keys():
            linestring=json.dumps(runopts['attachfailurelog'][dltype][url])+","+url
            attachmentfile.write(linestring+"\n")
        attachmentfile.close()

        if os.path.isfile(logfile):
            os.remove(logfile)
        shutil.copyfile(logfile+".1",logfile)
        os.remove(logfile+".1")

def addAttachmentLog(url,dltype,logfolder,runopts):
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)

    attachmentfile = open(driveutils.buildPath(logfolder,dltype+".txt"), 'a', encoding="utf8")
    attachmentfile.write(url+"\n")
    attachmentfile.close()

    attachlog=runopts['attachlog']
    attachlog[dltype].append(url)

#def addAttachmentFailureLog(url,dltype,logfolder,exception,runopts):
#    if not os.path.exists(logfolder):
#        os.makedirs(logfolder)
#
#    attachmentfile = open(driveutils.buildPath(logfolder,dltype+".fails.txt"), 'a', encoding="utf8")
#    attachmentfile.write(url+"\n")
#    attachmentfile.close()
#
#    attachlog=runopts['attachlog']
#    attachlog[dltype].append(url)

def checkInAttachmentFailureLog(url,dltype,runopts):
    if dltype not in runopts['attachfailurelog'].keys():
        return True
    if url not in runopts['attachfailurelog'][dltype].keys():
        return True
    if 'errs' not in runopts['attachfailurelog'][dltype][url].keys():
        return True
    errobj=runopts['attachfailurelog'][dltype][url]['errs']

    exceptionlist=[['HTTP Error 404: Not Found',5]]
    for exceptset in exceptionlist:
        if dltype in runopts['attachfailurechecklog'].keys():
            if url in runopts['attachfailurechecklog'][dltype].keys():
                if 'errs' in runopts['attachfailurechecklog'][dltype][url].keys():
                    if exceptset[0] in runopts['attachfailurechecklog'][dltype][url]['errs'].keys():
                        if runopts['attachfailurechecklog'][dltype][url]['errs'][exceptset[0]]:
                            return False
        if exceptset[0] in errobj.keys():
            if errobj[exceptset[0]] > exceptset[1]:
                return False
    return True


def checkInAttachmentLog(url,dltype,runopts):
    attachlog=runopts['attachlog']
#    print(url,len(attachlog[dltype]),(url in attachlog[dltype]))
    if url in attachlog[dltype]:
        return True
    return False

def getAttachments(filename,folderpath,dltype,logfolder,runopts):
    # Downloads attachments to the architecture - "<home>\BackupSelf\DiscordAttachmentBackups"
    # Logs successful downloads and failure counts to "<home>\BackupSync\DiscordChatBackups\discordattachlog"
    # The autobackup programs save the results to "<path to repos>/SYNC_DUMP/DISCORD_DUMP"
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

#    print ('-dl:',filename)
    with open(filename,'r',encoding="utf8") as f:
        for rline in f.readlines():
            rline=rline.rstrip()
            matchreg=".*=\s*\"https\:\/\/cdn\.discordapp\.com\/"+dltype+"\/[\/\.\w\-]+[\"']"
            if re.match(matchreg,rline):
                findreg1="[\"'](https\:\/\/cdn\.discordapp\.com\/"+dltype+"\/[\/\.\w\-]+)[\"']"
                url=re.findall(findreg1,rline)[0]
                if url is not None:

                    if not checkInAttachmentFailureLog(url,dltype,runopts):
                        continue

                    findregstart="[\"']https\:\/\/cdn\.discordapp\.com\/"+dltype
                    findreg2=re.compile(findregstart+"\/([\/\.\w\\\-]+)[\\\/][\.\w\-]+[\"']")
                    findreg3=re.compile(findregstart+"\/[\/\.\w\\\-]+[\\\/]([\.\w\-]+)[\"']")
                    urlfolder=re.findall(findreg2,rline)[0]
                    urlfile=re.findall(findreg3,rline)[0]

#                    print (urlfolder,urlfile)
                    if not os.path.exists(driveutils.buildPath(folderpath,urlfolder)):
                        os.makedirs(driveutils.buildPath(folderpath,urlfolder))
#                    print ('x',(os.path.exists(driveutils.buildPath(folderpath,urlfolder,urlfile))),driveutils.buildPath(folderpath,urlfolder,urlfile))
                    if not os.path.exists(driveutils.buildPath(folderpath,urlfolder,urlfile)):
#                        print ('y',driveutils.buildPath(folderpath,urlfolder,urlfile))
                        if not checkInAttachmentLog(url,dltype,runopts):
#                           context = ssl._create_unverified_context()
#                            urllib.urlopen(url, context=context)
#                           urllib.urlretrieve(url, folderpath+urlfolder+urlfile)
#                           print ' - - attachment:',folderpath+urlfolder+urlfile


                            if '_dlcounter' not in runopts.keys():
                                runopts['_dlcounter']={'count':0,'loop':0,'curmax':-1,'max':9,'mvar':4,'wait':10,'wvar':3}
                            if runopts['_dlcounter']['curmax'] < 0:
                                runopts['_dlcounter']['curmax']=runopts['_dlcounter']['max']+random.randrange(0,runopts['_dlcounter']['mvar']+1)
                            runopts['_dlcounter']['count']+=1
                            if runopts['_dlcounter']['count'] >= runopts['_dlcounter']['curmax']:
                                timewait=runopts['_dlcounter']['wait']+random.randrange(0,runopts['_dlcounter']['wvar']+1)
                                print ('waiting...',timewait)
                                print('Before: %s' % time.ctime())
                                time.sleep(timewait)
                                print('After: %s\n' % time.ctime())
                                runopts['_dlcounter']['count']=0
                                runopts['_dlcounter']['curmax']=-1

                            print (" - - url:",url)
                            req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXX' })
                            req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11");

                            try:
                                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
                                res = urllib2.urlopen(req, context=gcontext)
                                info = res.read()
                            except urllib2.HTTPError as exception:
                                addAttachmentFailureLog(url,dltype,logfolder,str(exception),runopts)
                                print ('*****HTTP ERR*****',exception,url)
                                if runopts['verbose'] > 0:
                                    print (driveutils.buildPath(folderpath,urlfolder,urlfile))
                                continue
                            except urllib2.URLError as exception:
                                addAttachmentFailureLog(url,dltype,logfolder,str(exception),runopts)
                                print ('*****URL ERR*****',exception,url)
                                if runopts['verbose'] > 0:
                                    print (driveutils.buildPath(folderpath,urlfolder,urlfile))
                                continue


                            if len(urlfile) >= 260:
                                urlfile = urlfile[-259:]

                            try:
                                newfilepath=driveutils.buildPath(folderpath,urlfolder,urlfile)
                                attachmentfile = open(newfilepath, 'wb')
                                attachmentfile.write(info)
                                attachmentfile.close()

                                if os.path.exists(newfilepath):
                                    if(int(os.stat(newfilepath).st_size) > 0):
                                        addAttachmentLog(url,dltype,logfolder,runopts)
                                    else:
                                        print ('empty file')

                            except IOError as exception:
                                print ('*****IO ERR*****',exception)
                                print (url)
                                print (driveutils.buildPath(folderpath,urlfolder,urlfile))
                                print ('  **********',exception)
                                continue

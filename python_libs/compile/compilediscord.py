import imp, os, sys, hashlib, time, shutil, re
import csv
import filecmp

SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
discordconf = imp.load_source('discordconf', SCRIPTPATH+'/local_config/discordconf.py')
driveutils = imp.load_source('driveutils', SCRIPTPATH+'/python_libs/utils/log_utils.py')

def monthToNum(shortMonth):
    return{
            'Jan' : 1,
            'Feb' : 2,
            'Mar' : 3,
            'Apr' : 4,
            'May' : 5,
            'Jun' : 6,
            'Jul' : 7,
            'Aug' : 8,
            'Sep' : 9,
            'Oct' : 10,
            'Nov' : 11,
            'Dec' : 12
    }[shortMonth]

def parseTimeObj(postobjtime):
    timeobj={}
    timeobj['day']=postobjtime[0]
    timeobj['month']=monthToNum(postobjtime[1])

    timeobj['year']='20'+postobjtime[2]
    timeobj['hour']=postobjtime[3]
    if timeobj['hour'] != '12' and postobjtime[5] == "P":
        timeobj['hour'] = str(  int(timeobj['hour'])+12  )
    if timeobj['hour'] == '12' and postobjtime[5] == "A":
        timeobj['hour'] = '00'
    timeobj['minute']=postobjtime[4]

    if timeobj['month'] < 10:
        timeobj['month'] = '0'+str(timeobj['month'])
    else:
        timeobj['month'] = str(timeobj['month'])
    return timeobj

def getOldestString(oldesttimestr,newesttimestr):
    if newesttimestr is None:
        return oldesttimestr
    if oldesttimestr is None:
        return newesttimestr
    timeobj=parseTimeObj(oldesttimestr)
    timeobj2=parseTimeObj(newesttimestr)

    checkset=['year', 'month', 'day', 'hour', 'minute']
    for timetype in checkset:
        if int(timeobj[timetype]) > int(timeobj2[timetype]):
            return newesttimestr
        if int(timeobj[timetype]) < int(timeobj2[timetype]):
            return oldesttimestr
    return newesttimestr


def stringOverlapLength(a, b):
    return max(i for i in range(len(b)+1) if a.endswith(b[:i]))

def gatherLogListWalk(logfolder,matchkeys={},servername=None):
    filelist = driveutils.readDir(logfolder)
    filelist.sort()
    for filename in filelist:
        if os.path.isdir(logfolder+"/"+filename) and re.match("^\d{8}_\d{6}\s*$",filename):
            gatherLogListWalk(logfolder+"/"+filename,matchkeys,servername)
        elif os.path.isdir(logfolder+"/"+filename):
            gatherLogListWalk(logfolder+"/"+filename,matchkeys,filename)
        elif os.path.isfile(logfolder+"/"+filename) and re.match(".*\.txt$",filename):
            if servername not in matchkeys.keys():
                matchkeys[servername]={}
            keyid=re.findall("(.*)\.txt$",filename)[0]
            if keyid not in matchkeys[servername].keys():
                matchkeys[servername][keyid]=[]
            matchkeys[servername][keyid].append(logfolder+"/"+filename)
    return matchkeys

def segmentLog(logset,overallfolderpath,outputfolder,username,servername,channelname):
    outputpath=outputfolder+"pieces/"+username+"/"+servername+"/"+channelname+"/"
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    oldesttimestr=None
    for logitem in logset:
        if os.path.exists(logitem):
            print 'segment: ',logitem
            dname=re.findall("^.*discordexport\/tmp\/([^\/]+)\/.*$",logitem)[0]
            if username == dname:
                testtimestr=segmentLogPieces(logitem,outputpath,username,servername,channelname)
                oldesttimestr=getOldestString(testtimestr,oldesttimestr)
    return oldesttimestr

def rebuildLogs(overallfolderpath,outputfolder,username,servername,channelname,outputpath):
    segmentspath=outputfolder+"segments/"+username+"/"+servername+"/"+channelname+"/"
    discordlogs=overallfolderpath+"discordlogs/"+username+"/"+servername+"/"+channelname+"/"
    if not os.path.exists(discordlogs):
        os.makedirs(discordlogs)

    print 'start build: ',segmentspath
    filelist = driveutils.readDir(segmentspath)
    filelist.sort()

    for timefolder in filelist:
        folderpath = segmentspath+"/"+timefolder
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):

            d=re.findall("^(\d{4})(\d\d)(\d\d)\s*$",timefolder)[0]
            newlogpath=discordlogs+d[0]+"_"+d[1]+"_"+d[2]+".html"
            driveutils.createNewLog(newlogpath,False)
            print ' - build: ',d[0]+"_"+d[1]+"_"+d[2]+".html"

            loglist = driveutils.readDir(folderpath)
            loglist.sort()

            bodypiecelog = open(newlogpath, 'a')
            if os.path.isfile(segmentspath+"header.txt"):
                with open(segmentspath+"header.txt", 'r') as myfile:
                    dataA = myfile.read()
                bodypiecelog.write(dataA.rstrip()+"\n")


            for logitem in loglist:
                logpath = segmentspath+"/"+timefolder+"/"+logitem
                if os.path.isfile(logpath) and re.match("^\d{4}\.txt\s*$",logitem):
                    with open(logpath, 'r') as myfile:
                        dataH = myfile.read()
                    bodypiecelog.write(dataH.rstrip()+"\n")


            if os.path.isfile(segmentspath+"footer.txt"):
                with open(segmentspath+"footer.txt", 'r') as myfile:
                    dataB = myfile.read()
                bodypiecelog.write(dataB.rstrip()+"\n")
            bodypiecelog.close()


def overlapLogPieces(outputfolder,username,servername,channelname,outputpath):
    def writeOverlapClip(logpath,dataStr):
        bodypiecelog = open(logpath, 'a')
        bodypiecelog.write("---------------------------INSERT CLIP-------------------------------\n")
        bodypiecelog.write(dataStr)
        bodypiecelog.write("---------------------------END CLIP-------------------------------\n")
        bodypiecelog.close()
    def testAvatarChange(logitem,newlogpath,dataA,dataB):
        dataAav = re.sub(r"<img class=\"msg\-avatar\"\s*src=\"https\:\/\/cdn\.discordapp\.com\/avatars\/[\w\/\.]+\"\s*\/>","<img class=\"msg-avatar\" src=\"\" />",dataA)
        dataBav = re.sub(r"<img class=\"msg\-avatar\"\s*src=\"https\:\/\/cdn\.discordapp\.com\/avatars\/[\w\/\.]+\"\s*\/>","<img class=\"msg-avatar\" src=\"\" />",dataB)

        overlapABav = stringOverlapLength(dataAav,dataBav)
        overlapBAav = stringOverlapLength(dataBav,dataAav)

        if overlapABav == 0 and overlapBAav == 0 and len(dataB) != 0:
            writeOverlapClip(newlogpath,dataB)
            print logitem, 'insert clip', len(dataB)
            return 'carry on'
        elif overlapABav == overlapBAav and overlapABav == len(dataBav):
            print logitem, 'skip over Aav', overlapABav, overlapBAav, 'len: ',len(dataB),len(dataBav)
            return 'skip over'
        elif overlapABav > overlapBAav and overlapABav == len(dataBav):
            print logitem, 'skip over Bav', overlapABav, overlapBAav, 'len: ',len(dataB),len(dataBav)
            return 'skip over'
        elif overlapABav < overlapBAav and overlapBAav == len(dataBav):
            print logitem, 'skip over Cav', overlapABav, overlapBAav, 'len: ',len(dataB),len(dataBav)
            return 'skip over'
        elif overlapABav > overlapBAav:
            print logitem, 'append to end (av)', overlapABav, overlapBAav, 'len: ', len(dataBav), ' onto ', len(dataAav)

            # Fetch the INTERSECTION REGION's msg-avatar SRC contents
            Apreoverlap = len(dataAav) - overlapABav
            overlapavatararray =  re.findall("<img class=\"msg-avatar\" src=\"\" />",dataAav[Apreoverlap:len(dataAav)])
            overlapoldavatararray =  re.findall("<img class=\"msg-avatar\" src=\"[^<>\"]+\" />",dataA)
            del overlapoldavatararray[len(overlapavatararray):]

            # replace the second-region with the first-region's replaced avatar contents
            dataBsub = dataBav
            for imgitem in overlapoldavatararray:
                dataBsub = re.sub(r"<img class=\"msg\-avatar\"\s*src=\"\"\s*\/>",imgitem,dataBsub,1)

            # If there is an overlap now, combine
            overlapABsub = stringOverlapLength(dataA,dataBsub)
            if overlapABsub > 0:
                bodypiecelog = open(newlogpath, 'a')
                bodypiecelog.write(dataB[overlapABsub:])
                bodypiecelog.close()
            else:
                print logitem, 'insert clip (append to end fail)', len(dataB)
                return 'write overlap'
        else:
            print logitem, 'append to start (av)', overlapABav, overlapBAav, 'len: ', len(dataBav), ' onto ', len(dataAav)

            # Fetch the INTERSECTION REGION's msg-avatar SRC contents
            Bpreoverlap = len(dataBav) - overlapBAav
            overlapavatararray =  re.findall("<img class=\"msg-avatar\" src=\"\" />",dataBav[Bpreoverlap:len(dataBav)])
            overlapoldavatararray = re.findall("<img class=\"msg-avatar\" src=\"[^<>\"]+\" />",dataB)
            shiftout = len(overlapoldavatararray)-len(overlapavatararray)
            del overlapoldavatararray[:shiftout]

            # replace the second-region with the first-region's replaced avatar contents
            dataAsub = dataAav
            for imgitem in overlapoldavatararray:
                dataAsub = re.sub(r"<img class=\"msg\-avatar\"\s*src=\"\"\s*\/>",imgitem,dataAsub,1)

            # If there is an overlap now, combine
            overlapBAsub = stringOverlapLength(dataB,dataAsub)
            if overlapBAsub > 0:
                if os.path.isfile(newlogpath+".2"):
                    os.remove(newlogpath+".2")

                bodypiecelog = open(newlogpath+".2", 'a')
                bodypiecelog.write(dataB)
                bodypiecelog.write(dataA[overlapBAsub:])
                bodypiecelog.close()

                os.remove(newlogpath)
                shutil.copyfile(newlogpath+".2",newlogpath)
                os.remove(newlogpath+".2")
            else:
                print logitem, 'insert clip (append to start fail)', len(dataB)
                return 'write overlap'
        return 'carry on'

    segmentspath=outputfolder+"segments/"+username+"/"+servername+"/"+channelname+"/"
    if not os.path.exists(segmentspath):
        os.makedirs(segmentspath)

    if os.path.isfile(segmentspath+"header.txt"):
        os.remove(segmentspath+"header.txt")
    if os.path.isfile(segmentspath+"footer.txt"):
        os.remove(segmentspath+"footer.txt")
    if os.path.isfile(outputpath+"header.txt"):
        shutil.copyfile(outputpath+"header.txt",segmentspath+"header.txt")
    if os.path.isfile(outputpath+"footer.txt"):
        shutil.copyfile(outputpath+"footer.txt",segmentspath+"footer.txt")

    print 'start merge: ',outputpath
    filelist = driveutils.readDir(outputpath)
    filelist.sort()

    for timefolder in filelist:
        folderpath = outputpath+"/"+timefolder
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):
            lastname = None
            loglist = driveutils.readDir(folderpath)
            loglist.sort()

            print ' - merge: ',timefolder
            for logitem in loglist:
                logpath = outputpath+"/"+timefolder+"/"+logitem
                if os.path.isfile(logpath) and re.match("^\d{4}\.\d+\.txt\s*$",logitem):
                    s=re.findall("^(\d{4})\.(\d+)\.txt\s*$",logitem)[0]
                    s0=int(s[0])
                    s1=int(s[1])

                    newlogpath = segmentspath+timefolder+"/"+s[0]+".txt"
                    if lastname is None or lastname != s0:
                        if not os.path.exists(segmentspath+timefolder):
                            os.makedirs(segmentspath+timefolder)
                        driveutils.createNewLog(newlogpath,False)
                    lastname = s0

                    with open(newlogpath, 'r') as myfile:
                        dataA = myfile.read()
                    with open(logpath, 'r') as myfile2:
                        dataB = myfile2.read()

                    if len(dataA) == 0 and len(dataB) != 0:
                        bodypiecelog = open(newlogpath, 'a')
                        bodypiecelog.write(dataB.rstrip()+"\n")
                        bodypiecelog.close()
                    else:
                        # Test if
                        overlapAB = stringOverlapLength(dataA,dataB)
                        overlapBA = stringOverlapLength(dataB,dataA)
                        if overlapAB == 0 and overlapBA == 0 and len(dataB) != 0:

                            # test msg-avatar changes
                            action = testAvatarChange(logitem,newlogpath,dataA,dataB)
                            if action == 'skip over':
                                continue
                            if action == 'write overlap':
                                writeOverlapClip(newlogpath,dataB)

                        elif overlapAB == overlapBA and overlapAB == len(dataB):
                            print logitem, 'skip over A', overlapAB, overlapBA, 'len: ', len(dataB)
                            continue
                        elif overlapAB > overlapBA and overlapAB == len(dataB):
                            print logitem, 'skip over B', overlapAB, overlapBA, 'len: ', len(dataB)
                            continue
                        elif overlapAB < overlapBA and overlapBA == len(dataB):
                            print logitem, 'skip over C', overlapAB, overlapBA, 'len: ', len(dataB)
                            continue
                        elif overlapAB > overlapBA:
                            print logitem, 'append to end', overlapAB, overlapBA, 'len: ', len(dataB), ' onto ', len(dataA)
                            bodypiecelog = open(newlogpath, 'a')
                            bodypiecelog.write(dataB[overlapAB:])
                            bodypiecelog.close()
                        else:
                            print logitem, 'append to start', overlapAB, overlapBA, 'len: ', len(dataB), ' onto ', len(dataA)
                            if os.path.isfile(newlogpath+".2"):
                                os.remove(newlogpath+".2")

                            bodypiecelog = open(newlogpath+".2", 'a')
                            bodypiecelog.write(dataB)
                            bodypiecelog.write(dataA[overlapBA:])
                            bodypiecelog.close()

                            os.remove(newlogpath)
                            shutil.copyfile(newlogpath+".2",newlogpath)
                            os.remove(newlogpath+".2")

def killOldestLogPieces(outputpath,oldesttimestr):
    if oldesttimestr is None:
        return
    timeobj=parseTimeObj(oldesttimestr)


    print 'start oldestkill: ',outputpath
    filelist = driveutils.readDir(outputpath)
    filelist.sort()

    killFolderList=[]
    for timefolder in filelist:
        folderpath = outputpath+"/"+timefolder
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):
            s=re.findall("^(\d{4})(\d\d)(\d\d)\s*$",timefolder)[0]
            s0=int(s[0])
            s1=int(s[1])
            s2=int(s[2])
            foldertimeobj={'year':s0,'month':s1,'day':s2}
            killThis=False
            compareset=['year','month','day']
            for timetype in compareset:
                if foldertimeobj[timetype] < int(timeobj[timetype]):
                    killThis=True
                    break
                if foldertimeobj[timetype] > int(timeobj[timetype]):
                    break
            if killThis:
                killFolderList.append(folderpath)
    for folderpath in killFolderList:
        try:
            print " - remove old directory: ",folderpath
            shutil.rmtree(folderpath)
        except OSError as exception:
            print '** err on '+str(exception)

def killDupeLogPieces(outputpath):
    print 'start dupekill: ',outputpath
    filelist = driveutils.readDir(outputpath)
    filelist.sort()

    for timefolder in filelist:
        folderpath = outputpath+"/"+timefolder
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):
            loglist = driveutils.readDir(folderpath)
            loglist.sort()

            a=0
            killAlist={}
            print ' - dupekill check: ',folderpath
            for logitem in loglist:
                logpath = outputpath+"/"+timefolder+"/"+logitem
                if os.path.isfile(logpath) and re.match("^\d{4}\.\d+\.txt\s*$",logitem):
                    s=re.findall("^(\d{4})\.(\d+)\.txt\s*$",logitem)[0]
                    s0=int(s[0])
                    s1=int(s[1])
                    # If the current log is already in the kill list, don't compare it for dupes
                    if s0 in killAlist.keys() and s1 in killAlist[s0].keys():
                        continue

                    for b in range((a+1), len(loglist) ):
                        logitem2 = loglist[b]
                        logpath2 = outputpath+"/"+timefolder+"/"+logitem2
                        if os.path.isfile(logpath2) and re.match("^\d{4}\.\d+\.txt\s*$",logitem2):
                            t=re.findall("^(\d{4})\.(\d+)\.txt\s*$",logitem2)[0]
                            t0=int(t[0])
                            t1=int(t[1])
                            if s0 == t0 and logpath != logpath2:
                                if t0 not in killAlist.keys() or t1 not in killAlist[t0].keys():
                                    if filecmp.cmp(logpath, logpath2):
                                        if t0 not in killAlist.keys():
                                            killAlist[t0]={}
                                        killAlist[t0][t1]=logpath2
                a=a+1

            sortedkeysA = killAlist.keys()
            sortedkeysA.sort()
            for a in sortedkeysA:
                sortedkeysB = killAlist[a].keys()
                sortedkeysB.sort()
                for b in sortedkeysB:
                    itemB = killAlist[a][b]
                    os.remove(itemB)

def segmentLogPieces(logitem,outputpath,username,servername,channelname):

    def writePostObject(postobj,outputpath):
        timeobj=parseTimeObj(postobj['time'])

        folderpath = outputpath + timeobj['year']+timeobj['month']+timeobj['day']+"/"
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        filepath = folderpath+timeobj['hour']+timeobj['minute']

        c=0
        while os.path.exists(filepath+"."+str(c)+".txt"):
            c=c+1

        curtimestr = timeobj['year']+timeobj['month']+timeobj['day']+"_"+timeobj['hour']+timeobj['minute']
        if postobj['last'] is None or postobj['last'] != curtimestr:
            c=c
            postobj['last']=curtimestr
            postobj['lastc']=c
        else:
            c=postobj['lastc']

        filepath = filepath+"."+str(c)+".txt"

        driveutils.createNewLog(filepath,True)
        bodypiecelog = open(filepath, 'a')
        for line in postobj['contents']:
            bodypiecelog.write(line.rstrip()+"\n")
        bodypiecelog.close()



    driveutils.createNewLog(outputpath+"/header.txt",False)
    headerlog = open(outputpath+"/header.txt", 'a')

    driveutils.createNewLog(outputpath+"/footer.txt",False)
    footerlog = open(outputpath+"/footer.txt", 'a')

    filemode="header"
    readmode="open"

    lasttimestr=None
    oldesttimestr=None
    postcount=0
    objreader={'contents':[],'text':[],'last':lasttimestr}
    with open(logitem,'rb') as f:
        for rline in f.readlines():
            if filemode!="footer" and re.match("^\s*<\/body>\s*$",rline):

                if readmode == "writing":
                    # save last posts, and remove trailing divs (cannot locate these reliably during loading)
                    if 'content' in objreader.keys() and len(objreader['contents']) > 2:
                        if re.match("^\s*<\/div>\s*$",objreader['contents'][-1]):
                            del objreader['contents'][-1]
                        if re.match("^\s*<\/div>\s*$",objreader['contents'][-1]):
                            del objreader['contents'][-1]
                    oldesttimestr=getOldestString(objreader['time'],oldesttimestr)
                    writePostObject(objreader,outputpath)
                    lasttimestr=objreader['last']
                    postcount=postcount+1


                footerlog.write("</div>\n</div>\n")
                filemode="footer"

            if filemode=="header":
                headerlog.write(rline.rstrip()+"\n")
            if filemode=="footer":
                footerlog.write(rline.rstrip()+"\n")
            if filemode=="body":
                if readmode == "open":
                    if re.match("^\s*<div class=\"msg\">\s*$",rline):
                        objreader={'contents':[],'text':[],'last':lasttimestr}
                        readmode = "writing"

                    objreader['contents'].append(rline.rstrip())
                elif readmode == "writing":
                    if re.match("^\s*<div class=\"msg\">\s*$",rline):
                        oldesttimestr=getOldestString(objreader['time'],oldesttimestr)
                        writePostObject(objreader,outputpath)
                        lasttimestr=objreader['last']
                        postcount=postcount+1
                        objreader={'contents':[],'text':[],'last':lasttimestr,'lastc':objreader['lastc']}

                    if re.match("<span class=\"msg\-date\">[^\<\>]+<\/span>",rline):
                        parts=re.findall("(?<=\"msg\-date\">)(\d\d)\-(\w+)-(\d\d) (\d\d)\:(\d\d) ([AP])M(?=<)",rline)
                        objreader['time']=parts[0]
                    if re.match("<span class=\"msg\-user\" title=.*<\/span>",rline):
                        parts=re.findall("<span class=\"msg\-user\" title=\"([^\"\<\>]+\#\d+)\">([^\"\<\>]+)<\/span>",rline)
                        objreader['user']=parts[0]
                    if re.match("<div class=\"msg\-content\">",rline):
                        objreader['text'].append(rline.rstrip())
                        readmode = "savetext"

                    objreader['contents'].append(rline.rstrip())
                elif readmode == "savetext":
                    if re.match(".*<\/div>\s*$",rline):
                        readmode = "writing"
                    objreader['text'].append(rline.rstrip())
                    objreader['contents'].append(rline.rstrip())


            if filemode=="header" and re.match("^\s*<div id=\"log\">\s*$",rline):
                filemode="body"

    f.close()
    headerlog.close()
    footerlog.close()
    if postcount > 1000:
        return oldesttimestr
    return None

def archiveLogs(logset,archivepath,outputfolder):
    if not os.path.exists(archivepath):
        os.makedirs(archivepath)

    for logitem in logset:
        if os.path.exists(logitem):
            namepieces=re.findall("^.*\/tmp\/[^\/]+\/+(\d{8}_\d{6})\/[^\/]+\/([^\/]+)\.txt\s*$",logitem)[0]
            filename=namepieces[1]+"-"+namepieces[0]+".txt"

            if not os.path.exists(archivepath+filename):
                print 'copy to : ',archivepath+filename
                shutil.copyfile(logitem,archivepath+filename)
#            os.remove(logitem)
    filelist = driveutils.readDir(archivepath)
    filelist.sort()

    a=0
    cleanList=[]
    for filename in filelist:
        filepath = archivepath+filename
        if os.path.isfile(filepath) and filepath not in cleanList:
            for b in range((a+1), len(filelist) ):
                filename2 = filelist[b]
                filepath2 = archivepath+filename2
                if os.path.isfile(filepath2) and filepath2 not in cleanList:
                    if filecmp.cmp(filepath, filepath2) and filepath != filepath2:
                        cleanList.append(filepath2)
        a=a+1
    for path in cleanList:
        print "removing: ", path
        os.remove(path)

def clearEmptyTmps(outputfolder,username):
    def walkAndClear(path):
        filelist = driveutils.readDir(path)
        if len(filelist) == 0:
            try:
                print "remove empty directory: ",path
                shutil.rmtree(path)
            except OSError as exception:
                print '** err on '+str(exception)
        else:
            for name in filelist:
                namepath = path+"/"+name
                if os.path.isdir(namepath):
                    walkAndClear(namepath)

    exportfolder=outputfolder+"tmp/"+username+"/"
    filelist = driveutils.readDir(exportfolder)
    for datename in filelist:
        datepath = exportfolder+datename
        if os.path.isdir(datepath):
            walkAndClear(datepath)

def compileDiscordLogs(overallfolderpath,runopts):
    if 'nocompile' in runopts.keys():
        if runopts['nocompile'] == True:
            return

    outputfolder=overallfolderpath+"discordexport/"
    exportfolder=overallfolderpath+"discordexport/tmp/"


    for username,tokenuserset in discordconf.IMPORTDICT.iteritems():
        if os.path.exists(exportfolder+username):
            targetlogs={}
            targetlogs=gatherLogListWalk((exportfolder+username),{})
            print targetlogs.keys()
            print '---------'
            continue
            oldesttimestr=None
            for servername,serverset in targetlogs.iteritems():
                for channelname,logset in targetlogs[servername].iteritems():
                    print '========= BEGIN: ',username,servername,channelname,'========='
                    oldesttimestr=segmentLog(logset,overallfolderpath,outputfolder,username,servername,channelname)

                    outputpath=outputfolder+"pieces/"+username+"/"+servername+"/"+channelname+"/"

                    if 'compileonly' not in runopts.keys() or runopts['compileonly'] == False:
                        killOldestLogPieces(outputpath,oldesttimestr)

                    killDupeLogPieces(outputpath)
                    overlapLogPieces(outputfolder,username,servername,channelname,outputpath)
                    rebuildLogs(overallfolderpath,outputfolder,username,servername,channelname,outputpath)

                    print '========= CLEANUP: ',username,servername,channelname,'========='
                    archivepath=outputfolder+"archive/"+username+"/"+servername+"/"+channelname+"/"
                    archiveLogs(logset,archivepath,outputfolder)
            clearEmptyTmps(outputfolder,username)

import imp, os, sys, hashlib, time, shutil, re, pathlib
import csv
import filecmp

_SUBSCRIPTPATH = os.path.join(*list(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parts[0:-2]))

attachmentsdiscord = imp.load_source('attachmentsdiscord', os.path.join(_SUBSCRIPTPATH,'python_libs','discord','attachmentsdiscord.py'))
discordconf = imp.load_source('discordconf', os.path.join(_SUBSCRIPTPATH,'local_config','discordconf.py'))
driveutils = imp.load_source('driveutils', os.path.join(_SUBSCRIPTPATH,'python_libs','utils','log_utils.py'))

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

    if len(postobjtime) > 3:
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


def rebuildLogs(overallfolderpath,tmpoutputfolder,username,servername,channelname,runopts):
    # builds the dates by using the segments/ content and writing .html.bak files to the discordchatlogs/
    segmentspath=driveutils.buildPath(tmpoutputfolder,"tmp","segments",username,servername,channelname)
    discordlogs=driveutils.buildPath(overallfolderpath,"discordchatlogs",username,servername,channelname)
    if not os.path.exists(discordlogs):
        os.makedirs(discordlogs)

    filelist = driveutils.readDir(segmentspath)
    filelist.sort()

    for timefolder in filelist:
        folderpath = driveutils.buildPath(segmentspath,timefolder)
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):

            d=re.findall("^(\d{4})(\d\d)(\d\d)\s*$",timefolder)[0]
            newlogpath=driveutils.buildPath(discordlogs,d[0]+"_"+d[1]+"_"+d[2]+".html.bak")
            driveutils.createNewLog(newlogpath,False)
            if runopts['verbose'] > 0:
                print (' - build: '+driveutils.buildPath(discordlogs,d[0]+"_"+d[1]+"_"+d[2]+".html"))

            loglist = driveutils.readDir(folderpath)
            loglist.sort()

            bodypiecelog = open(newlogpath, 'a', encoding="utf8")
            if os.path.isfile(driveutils.buildPath(segmentspath,"header.txt")):
                with open(driveutils.buildPath(segmentspath,"header.txt"), 'r', encoding="utf8") as myfile:
                    dataA = myfile.read()
                bodypiecelog.write(dataA.rstrip()+"\n")


            for logitem in loglist:
                logpath = driveutils.buildPath(segmentspath,timefolder,logitem)
                if os.path.isfile(logpath) and re.match("^\d{4}\.txt\s*$",logitem):
                    with open(logpath, 'r', encoding="utf8") as myfile:
                        dataH = myfile.read()
                    bodypiecelog.write(dataH.rstrip()+"\n")


            if os.path.isfile(driveutils.buildPath(segmentspath,"footer.txt")):
                with open(driveutils.buildPath(segmentspath,"footer.txt"), 'r', encoding="utf8") as myfile:
                    dataB = myfile.read()
                bodypiecelog.write(dataB.rstrip()+"\n")
            bodypiecelog.close()

            targetlogpath=driveutils.buildPath(discordlogs,d[0]+"_"+d[1]+"_"+d[2]+".html")
            if os.path.isfile(targetlogpath):
                os.remove(targetlogpath)
            shutil.copyfile(newlogpath,targetlogpath)
            os.remove(newlogpath)


def overlapLogPieces(tmpoutputfolder,username,servername,channelname,outputpath):
    # builds the header.txt, footer.txt files in the segments/ folders
    def writeOverlapClip(logpath,dataStr):
        bodypiecelog = open(logpath, 'a', encoding="utf8")
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
#            print logitem, 'insert clip', len(dataB)
            return 'carry on'
        elif overlapABav == overlapBAav and overlapABav == len(dataBav):
#            print logitem, 'skip over Aav', overlapABav, overlapBAav, 'len: ',len(dataB),len(dataBav)
            return 'skip over'
        elif overlapABav > overlapBAav and overlapABav == len(dataBav):
#            print logitem, 'skip over Bav', overlapABav, overlapBAav, 'len: ',len(dataB),len(dataBav)
            return 'skip over'
        elif overlapABav < overlapBAav and overlapBAav == len(dataBav):
#            print logitem, 'skip over Cav', overlapABav, overlapBAav, 'len: ',len(dataB),len(dataBav)
            return 'skip over'
        elif overlapABav > overlapBAav:
#            print logitem, 'append to end (av)', overlapABav, overlapBAav, 'len: ', len(dataBav), ' onto ', len(dataAav)

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
                bodypiecelog = open(newlogpath, 'a', encoding="utf8")
                bodypiecelog.write(dataB[overlapABsub:])
                bodypiecelog.close()
            else:
#                print logitem, 'insert clip (append to end fail)', len(dataB)
                return 'write overlap'
        else:
#            print logitem, 'append to start (av)', overlapABav, overlapBAav, 'len: ', len(dataBav), ' onto ', len(dataAav)

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

                bodypiecelog = open(newlogpath+".2", 'a', encoding="utf8")
                bodypiecelog.write(dataB)
                bodypiecelog.write(dataA[overlapBAsub:])
                bodypiecelog.close()

                os.remove(newlogpath)
                shutil.copyfile(newlogpath+".2",newlogpath)
                os.remove(newlogpath+".2")
            else:
#                print logitem, 'insert clip (append to start fail)', len(dataB)
                return 'write overlap'
        return 'carry on'

    segmentspath=driveutils.buildPath(tmpoutputfolder,"tmp","segments",username,servername,channelname)
    clearTmpFolders(segmentspath,True)

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

#    print 'start merge: ',outputpath
    filelist = driveutils.readDir(outputpath)
    filelist.sort()

    for timefolder in filelist:
        folderpath = driveutils.buildPath(outputpath,timefolder)
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):
            lastname = None
            loglist = driveutils.readDir(folderpath)
            loglist.sort()

#            print ' - merge: ',timefolder
            for logitem in loglist:
                logpath = driveutils.buildPath(outputpath,timefolder,logitem)
                if os.path.isfile(logpath) and re.match("^\d{4}\.\d+\.txt\s*$",logitem):
                    s=re.findall("^(\d{4})\.(\d+)\.txt\s*$",logitem)[0]
                    s0=int(s[0])
                    s1=int(s[1])

                    newlogpath = driveutils.buildPath(segmentspath,timefolder,s[0]+".txt")
                    if lastname is None or lastname != s0:
                        if not os.path.exists(driveutils.buildPath(segmentspath,timefolder)):
                            os.makedirs(driveutils.buildPath(segmentspath,timefolder))
                        driveutils.createNewLog(newlogpath,False)
                    lastname = s0

                    with open(newlogpath, 'r', encoding="utf8") as myfile:
                        dataA = myfile.read()
                    with open(logpath, 'r', encoding="utf8") as myfile2:
                        dataB = myfile2.read()

                    if len(dataA) == 0 and len(dataB) != 0:
                        bodypiecelog = open(newlogpath, 'a', encoding="utf8")
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
#                            print logitem, 'skip over A', overlapAB, overlapBA, 'len: ', len(dataB)
                            continue
                        elif overlapAB > overlapBA and overlapAB == len(dataB):
#                            print logitem, 'skip over B', overlapAB, overlapBA, 'len: ', len(dataB)
                            continue
                        elif overlapAB < overlapBA and overlapBA == len(dataB):
#                            print logitem, 'skip over C', overlapAB, overlapBA, 'len: ', len(dataB)
                            continue
                        elif overlapAB > overlapBA:
#                            print logitem, 'append to end', overlapAB, overlapBA, 'len: ', len(dataB), ' onto ', len(dataA)
                            bodypiecelog = open(newlogpath, 'a', encoding="utf8")
                            bodypiecelog.write(dataB[overlapAB:])
                            bodypiecelog.close()
                        else:
#                            print logitem, 'append to start', overlapAB, overlapBA, 'len: ', len(dataB), ' onto ', len(dataA)
                            if os.path.isfile(newlogpath+".2"):
                                os.remove(newlogpath+".2")

                            bodypiecelog = open(newlogpath+".2", 'a', encoding="utf8")
                            bodypiecelog.write(dataB)
                            bodypiecelog.write(dataA[overlapBA:])
                            bodypiecelog.close()

                            os.remove(newlogpath)
                            shutil.copyfile(newlogpath+".2",newlogpath)
                            os.remove(newlogpath+".2")

def archiveLogs(logset,archivepath,outputfolder):
    return
    # CURRENTLY DEFUNCT
    if not os.path.exists(archivepath):
        os.makedirs(archivepath)

    for logitem in logset:
        if os.path.exists(logitem):
            namepieces=re.findall("^.*\/tmp\/exported\/[^\/]+\/+(\d{8}_\d{6})\/[^\/]+\/([^\/]+)\.txt\s*$",logitem)[0]
            filename=namepieces[1]+"-"+namepieces[0]+".txt"

            if not os.path.exists(driveutils.buildPath(archivepath,filename)):
                print ('copy to : ',driveutils.buildPath(archivepath,filename))
                shutil.copyfile(logitem,driveutils.buildPath(archivepath,filename))
#            os.remove(logitem)
    filelist = driveutils.readDir(archivepath)
    filelist.sort()

    a=0
    cleanList=[]
    for filename in filelist:
        filepath = driveutils.buildPath(archivepath,filename)
        if os.path.isfile(filepath) and filepath not in cleanList:
            for b in range((a+1), len(filelist) ):
                filename2 = filelist[b]
                filepath2 = driveutils.buildPath(archivepath,filename2)
                if os.path.isfile(filepath2) and filepath2 not in cleanList:
                    if filecmp.cmp(filepath, filepath2) and filepath != filepath2:
                        cleanList.append(filepath2)
        a=a+1
    for path in cleanList:
        os.remove(path)

def clearTmpFolders(folderpath,rebuild):
    try:
        if os.path.exists(folderpath):
#            print (" - remove old directory: ",folderpath)
            shutil.rmtree(folderpath)
    except OSError as exception:
        print ('** err on '+str(exception))
    if rebuild:
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)


def writePostObject(postobj,outputpath):
    timeobj=parseTimeObj(postobj['time'])

    folderpath = driveutils.buildPath(outputpath,timeobj['year']+timeobj['month']+timeobj['day'])
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    filepath = driveutils.buildPath(folderpath,timeobj['hour']+timeobj['minute'])

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

    bodypiecelog = open(filepath, 'a', encoding="utf8")
    for line in postobj['contents']:
        bodypiecelog.write(line.rstrip()+"\n")
    bodypiecelog.close()

def divideUpLog(logitem,outputpath,username,servername,channelname):
    driveutils.createNewLog(driveutils.buildPath(outputpath,"header.txt"),False)
    headerlog = open(driveutils.buildPath(outputpath,"header.txt"), 'a', encoding="utf8")

    driveutils.createNewLog(driveutils.buildPath(outputpath,"footer.txt"),False)
    footerlog = open(driveutils.buildPath(outputpath,"footer.txt"), 'a', encoding="utf8")

    driveutils.createNewLog(driveutils.buildPath(outputpath,"body.txt"),False)
    bodylog = open(driveutils.buildPath(outputpath,"body.txt"), 'a', encoding="utf8")

    filemode = "header"
    readmode = "savetext"
    divcount = 0
    heldtext = ""


    with open(logitem,'r', encoding="utf8") as f:
        for rline in f.readlines():
            if filemode!="footer" and re.match("^\s*<\/body>\s*$",rline):
                footerlog.write("</div>\n")
                filemode="footer"

            if filemode=="header":
                headerlog.write(rline.rstrip()+"\n")
            if filemode=="footer":
                footerlog.write(rline.rstrip()+"\n")
            if filemode=="body":
                if re.match("^\s*<\/div>\s*$",rline):
                    divcount=divcount+1
                    if divcount < 3:
                        heldtext+=rline.rstrip()+"\n"

                elif re.match("^.*<\/div>\s*$",rline):
                    divcount=1
                    heldtext = ""
                    bodylog.write(rline.rstrip()+"\n")
                else:
                    if len(heldtext) > 1:
                        bodylog.write(heldtext.rstrip()+"\n")
                    bodylog.write(rline.rstrip()+"\n")
                    heldtext = ""
                    divcount = 0

            if filemode=="header" and re.match("^\s*<div (?:class|id)=\"(?:chat)?log\">\s*$",rline):
                filemode="body"

def segmentLogPieces(outputpath,username,servername,channelname):
    # breaks the body output from 'body.txt'
    # output is saved to '<outputpath>/<date>/<time>.<num>.txt'
    readmode="open"

    lasttimestr=None
    oldesttimestr=None
    objreader={'contents':[],'text':[],'last':lasttimestr}
    with open(driveutils.buildPath(outputpath,"body.txt"),'r', encoding="utf8") as f:
        for rline in f.readlines():
            if readmode == "open":
                if re.match("^\s*<div class=\"chatlog__message-group\">\s*$",rline):
                    objreader={'contents':[],'text':[],'last':lasttimestr}
                    readmode = "writing"

                objreader['contents'].append(rline.rstrip())
            elif readmode == "writing":
                if re.match("^\s*<div class=\"chatlog__message-group\">\s*$",rline):
                    if 'time' in objreader.keys():
                        writePostObject(objreader,outputpath)
                    lasttimestr=objreader['last']
                    objreader={'contents':[],'text':[],'last':lasttimestr,'lastc':objreader['lastc']}

                if re.match("\s*<span class=\"chatlog__timestamp\">[^\<\>]+<\/span>\s*",rline):
                    parts=re.findall("(?<=\"chatlog__timestamp\">)(\d\d)\-(\w+)-(\d\d) (\d\d)\:(\d\d) ([AP])M(?=<)",rline)
                    objreader['time']=parts[0]
                if re.match("<span class=\"chatlog__author-name\" title=.*<\/span>",rline):
                    parts=re.findall("<span class=\"chatlog__author-name\" title=\"([^\"\<\>]+\#\d+)\">([^\"\<\>]+)<\/span>",rline)
                    objreader['user']=parts[0]
                if re.match("<div class=\"chatlog__content\">",rline):
                    objreader['text'].append(rline.rstrip())
                    readmode = "savetext"

                objreader['contents'].append(rline.rstrip())
            elif readmode == "savetext":
                if re.match(".*<\/div>\s*$",rline):
                    readmode = "writing"
                objreader['text'].append(rline.rstrip())
                objreader['contents'].append(rline.rstrip())


    # save last posts, and remove trailing divs (cannot locate these reliably during loading)
#                oldesttimestr=getOldestString(objreader['time'],oldesttimestr)
    if 'time' in objreader.keys():
        writePostObject(objreader,outputpath)
    lasttimestr=objreader['last']

    f.close()

def joinSegmentPieceLogs(tmpoutputfolder,segmentoutputpath,splitjoinpath,username,serverstr,channelstr):
    # JOIN NEW SEGMENT LOG PIECES WITH OLDER LOG PIECES
    # clears the splitjoin/ architecture (<home>\tmp\discordexport\tmp\splitjoin\<username>\<serverstr>\<channelstr>\<date>\<time>.<num>.txt)
    # copies oldsplit/ piece files into the splitjoin/ architecture, adding them to higher numbers if there's overlap
    # after, copies pieces/ piece files into the splitjoin/ architecture, adding them to higher numbers if there's overlap
    # if there were no piece files in the splitjoin/ architecture, copies all the pieces/ piece files there
    if not os.path.exists(splitjoinpath):
        os.makedirs(splitjoinpath)

    clearTmpFolders(splitjoinpath,True)

    piecespath=driveutils.buildPath(tmpoutputfolder,"tmp","pieces",username,serverstr,channelstr)
    segmentoldpath=driveutils.buildPath(tmpoutputfolder,"tmp","oldsplit",username,serverstr,channelstr)
#    print('pieces',piecespath)
#    print('segmentold',segmentoldpath)
    if os.path.exists(segmentoldpath):
        for datename in os.listdir(segmentoldpath):
            if os.path.isdir(driveutils.buildPath(segmentoldpath,datename)):
                if re.match("^\d+$",datename):

                    # only join/build old log dates if there's a new scan for them
#                    print('isdir',os.path.isdir(driveutils.buildPath(piecespath,datename)),driveutils.buildPath(piecespath,datename))
                    if os.path.isdir(driveutils.buildPath(piecespath,datename)):

                        # copies oldsplit/ piece files into the splitjoin/ architecture, adding them at a higher number if necessary
                        for piecename in os.listdir(driveutils.buildPath(segmentoldpath,datename)):
                            if not os.path.exists(driveutils.buildPath(splitjoinpath,datename)):
                                os.makedirs(driveutils.buildPath(splitjoinpath,datename))

                            if not os.path.exists(driveutils.buildPath(splitjoinpath,datename,piecename)):
                                shutil.copy(driveutils.buildPath(segmentoldpath,datename,piecename), driveutils.buildPath(splitjoinpath,datename,piecename))
#                                print ('oldpath newpiece',driveutils.buildPath(splitjoinpath,datename,piecename))
                            else:
                                timename=re.findall("^(\d+)",piecename).pop()
                                c=re.findall("^\d+\.(\d+)",piecename).pop()
                                c=int(c)
                                while os.path.exists(driveutils.buildPath(splitjoinpath,datename,timename+"."+str(c)+".txt")):
                                    c=c+1
                                newpiecename=timename+"."+str(c)+".txt"
                                shutil.copy(driveutils.buildPath(segmentoldpath,datename,piecename), driveutils.buildPath(splitjoinpath,datename,newpiecename))
#                                print ('oldpath appendpiece',driveutils.buildPath(splitjoinpath,datename,newpiecename))
    for datename in os.listdir(segmentoutputpath):
        if os.path.isdir(driveutils.buildPath(segmentoutputpath,datename)):
            if re.match("^\d+$",datename):
                # copies pieces/ piece files into the splitjoin/ architecture, adding them at a higher number if necessary
                for piecename in os.listdir(driveutils.buildPath(segmentoutputpath,datename)):
#                                    shutil.copytree(segmentoutputpath+datename, splitjoinpath)
                    if not os.path.exists(driveutils.buildPath(splitjoinpath,datename)):
                        os.makedirs(driveutils.buildPath(splitjoinpath,datename))

                    if not os.path.exists(driveutils.buildPath(splitjoinpath,datename,piecename)):
                        shutil.copy(driveutils.buildPath(segmentoutputpath,datename,piecename), driveutils.buildPath(splitjoinpath,datename))
#                        print ('outputpath newpiece',driveutils.buildPath(segmentoutputpath,datename,piecename))
                    else:
                        timename=re.findall("^(\d+)",piecename).pop()
                        c=re.findall("^\d+\.(\d+)",piecename).pop()
                        c=int(c)
                        while os.path.exists(driveutils.buildPath(splitjoinpath,datename,timename+"."+str(c)+".txt")):
                            c=c+1
                        newpiecename=timename+"."+str(c)+".txt"
                        shutil.copy(driveutils.buildPath(segmentoutputpath,datename,piecename), driveutils.buildPath(splitjoinpath,datename,newpiecename))
#                        print ('outputpath appendpiece',driveutils.buildPath(segmentoutputpath,datename,newpiecename))

        else:
            # if there were no piece files in the splitjoin/ architecture, copies all the pieces/ piece files there
            shutil.copy(driveutils.buildPath(segmentoutputpath,datename), driveutils.buildPath(splitjoinpath,datename))
#            print ('lastpiece',driveutils.buildPath(splitjoinpath,datename))


def getDiscordID(serverstr):
    findservid=re.findall("\-(\d+)\s*$",serverstr)
    if len(findservid) == 0:
        findservid=re.findall("^(\d+)\-",serverstr)
    thisserverid=None if len(findservid) == 0 else findservid.pop()
    return thisserverid

def filterDiscordIDs(thisid,type,runopts):
    if type in runopts.keys():
        if thisid is not None and thisid not in runopts[type]:
            return False
        if type == 'servid' and thisid is None and 'privatemessages' not in runopts[type]:
            return False
    return True

def downloadAllAttachmentsDiscordLogs(overallfolderpath,runopts):
    runopts['attachlog']=attachmentsdiscord.loadAttachmentLog(driveutils.buildPath(overallfolderpath,"discordattachlog"))
    runopts['attachfailurelog']=attachmentsdiscord.loadAttachmentFailureLog(driveutils.buildPath(overallfolderpath,"discordattachlog"))
    runopts['attachfailurechecklog']={}

    oldlogfolder=driveutils.buildPath(overallfolderpath,"discordchatlogs")
    for username in os.listdir(oldlogfolder):
        for serverstr in os.listdir(driveutils.buildPath(oldlogfolder,username)):

            thisserverid=getDiscordID(serverstr)
            if not filterDiscordIDs(thisserverid,'servid',runopts):
                continue

            for channelstr in os.listdir(driveutils.buildPath(oldlogfolder,username,serverstr)):
                thischannelid=getDiscordID(channelstr)
                if not filterDiscordIDs(thischannelid,'chanid',runopts):
                    continue

                print("@-",serverstr," ",channelstr)
                logpaths=driveutils.buildPath(oldlogfolder,username,serverstr,channelstr)
                attachmentsdiscord.buildAllAttachments(overallfolderpath,username,serverstr,channelstr,runopts)

def compileDiscordLogs(overallfolderpath,overalltmppath,runopts):
    def checkForValidMessageFormat(logpath):
        checkstr = None

        for i, line in enumerate(open(logpath, 'r', encoding="utf8")):
            for match in re.finditer( re.compile("\s*<div class=\"(chatlog__message-group)\">\s*"), line):
                checkstrobj=match.groups()
                if checkstrobj is None:
                    continue
                elif not isinstance(checkstrobj, tuple):
                    continue
                checkstr = checkstrobj[0]
                if checkstr is not None:
                    return True
        return False

    if 'nocompile' in runopts.keys():
        if runopts['nocompile'] == True:
            return


    oldlogfolder=driveutils.buildPath(overallfolderpath,"discordchatlogs")
    tmpoutputfolder=driveutils.buildPath(overalltmppath,"discordexport")
    exportfolder=driveutils.buildPath(overalltmppath,"discordexport","tmp","exported")

    runopts['attachlog']=attachmentsdiscord.loadAttachmentLog(driveutils.buildPath(overallfolderpath,"discordattachlog"))
    runopts['attachfailurelog']=attachmentsdiscord.loadAttachmentFailureLog(driveutils.buildPath(overallfolderpath,"discordattachlog"))
    runopts['attachfailurechecklog']={}

    for username in os.listdir(exportfolder):
        logpaths=driveutils.buildPath(exportfolder,username)
        for datedir in os.listdir(logpaths):
            datedirpath=driveutils.buildPath(logpaths,datedir)
            for serverstr in os.listdir(datedirpath):
                serverarr=serverstr.split("-")

                serverid=serverarr.pop(0)
                serversafename="-".join(serverarr)

                if not filterDiscordIDs(serverid,'servid',runopts):
                    continue

                serverfolderpath=driveutils.buildPath(datedirpath,serverstr)
                for channelstrfull in os.listdir(serverfolderpath):
                    channelstr=channelstrfull.rstrip(".txt")
                    channelarr=channelstrfull.rstrip(".txt").split("-")
                    channelid=channelarr.pop()
                    channelsafename="-".join(channelarr)

                    if not filterDiscordIDs(channelid,'chanid',runopts):
                        continue

                    print("@>",serversafename+"-"+serverid," ",channelstr)

                    piecesoutputpath=driveutils.buildPath(tmpoutputfolder,"tmp","pieces",username,serverstr,channelstr)
                    clearTmpFolders(piecesoutputpath,True)


                    discordlogpath = driveutils.buildPath(serverfolderpath,channelstrfull)
                    if runopts['verbose'] > 0:
                        print ('divide log: ',discordlogpath)


                    divideUpLog(discordlogpath,piecesoutputpath,username,serverstr,channelstr)

                    # breaks files inside '<home>\tmp\discordexport\tmp\pieces\<username>\<serverstr>\<channelstr>\body.txt'
                    # output is saved to '<home>\tmp\discordexport\tmp\pieces\<username>\<serverstr>\<channelstr>\<date>\<time>.<num>.txt'
                    testtimestr=segmentLogPieces(piecesoutputpath,username,serverstr,channelstr)
#                    print('.segment',piecesoutputpath)

                    checklog = checkForValidMessageFormat(driveutils.buildPath(piecesoutputpath,"body.txt"))
                    if checklog is None:
                        print ("ERR, log has no messages: ",discordlogpath)
                        sys.exit(0)

                    for datename in os.listdir(piecesoutputpath):
                        if os.path.isdir(driveutils.buildPath(piecesoutputpath,datename)):
                            if re.match("^\d+$",datename):
                                dateyear=re.findall("^(\d{4})",datename).pop()
                                datemonth=re.findall("^\d{4}(\d\d)",datename).pop()
                                dateday=re.findall("^\d{6}(\d\d)",datename).pop()

                                logcheckpath=driveutils.buildPath(oldlogfolder,username,serverstr,channelstr)
                                oldlogfile=driveutils.buildPath(logcheckpath,dateyear+"_"+datemonth+"_"+dateday+".html")
                                if os.path.isfile(oldlogfile):
                                    segmentoldsplitpath=driveutils.buildPath(tmpoutputfolder,"tmp","oldsplit",username,serverstr,channelstr)
                                    clearTmpFolders(driveutils.buildPath(segmentoldsplitpath,datename),True)

                                    if runopts['verbose'] > 0:
                                        print ('divide log: ',oldlogfile)
                                    divideUpLog(oldlogfile,segmentoldsplitpath,username,serverstr,channelstr)

                                    # breaks files inside '<home>\tmp\discordexport\tmp\oldsplit\<username>\<serverstr>\<channelstr>\body.txt'
                                    # output is saved to '<home>\tmp\discordexport\tmp\oldsplit\<username>\<serverstr>\<channelstr>\<date>\<time>.<num>.txt'
                                    segmentLogPieces(segmentoldsplitpath,username,serverstr,channelstr)
#                                    print(',segment',segmentoldsplitpath)

                                    checklog = checkForValidMessageFormat(driveutils.buildPath(segmentoldsplitpath,"body.txt"))
                                    if checklog is None:
                                        print ("ERR, log has no messages: ",oldlogfile)
                                        sys.exit(0)

#                    print('join segments from',tmpoutputfolder)
#                    print('join segments to',piecesoutputpath)

                    splitjoinpath=driveutils.buildPath(tmpoutputfolder,"tmp","splitjoin",username,serverstr,channelstr)
                    # output is saved to '<home>\tmp\discordexport\tmp\splitjoin\<username>\<serverstr>\<channelstr>\<date>\<time>.<num>.txt'
                    joinSegmentPieceLogs(tmpoutputfolder,piecesoutputpath,splitjoinpath,username,serverstr,channelstr)
                    # output is saved to '<home>\tmp\discordexport\tmp\segments\'
                    overlapLogPieces(tmpoutputfolder,username,serverstr,channelstr,splitjoinpath)
                    # output is saved to the discordchatlogs/
                    rebuildLogs(overallfolderpath,tmpoutputfolder,username,serverstr,channelstr,runopts)
                    attachmentsdiscord.buildAttachmentsFromTmp(overallfolderpath,tmpoutputfolder,username,serverstr,channelstr,runopts)


                    # loop over days
                    # see if any current logs exist for that days
                    # divide up log into a '/reserve/' folder, segment
                    # attempt to pack together bodies.  if fails, pack together pieces?
                    # push original log into /tmp/reserve/, replace with new

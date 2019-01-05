import imp, os, sys, hashlib, time, shutil, re
import csv
import filecmp
import urllib,ssl,urllib2

SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
driveutils = imp.load_source('driveutils', SCRIPTPATH+'/python_libs/utils/log_utils.py')

def buildAttachmentsFromTmp(overallfolderpath,tmpoutputfolder,username,servername,channelname):
    segmentspath=tmpoutputfolder+"tmp/segments/"+username+"/"+servername+"/"+channelname+"/"
    discordlogs=overallfolderpath+"discordlogs/"+username+"/"+servername+"/"+channelname+"/"

    if not os.path.exists(discordlogs):
        os.makedirs(discordlogs)

    filelist = driveutils.readDir(segmentspath)
    filelist.sort()

    for timefolder in filelist:
        folderpath = segmentspath+"/"+timefolder
        if os.path.isdir(folderpath) and re.match("^\d{8}\s*$",timefolder):
            if not os.path.exists(segmentspath+"/"+timefolder):
                os.makedirs(segmentspath+"/"+timefolder)

#            d=re.findall("^(\d{4})(\d\d)(\d\d)\s*$",timefolder)[0]

            loglist = driveutils.readDir(folderpath)
            loglist.sort()

            for logitem in loglist:
                logpath = segmentspath+"/"+timefolder+"/"+logitem
                if os.path.isfile(logpath) and re.match("^\d{4}\.txt\s*$",logitem):
                    getAttachments(logpath,discordlogs+"attachments/"+timefolder+"/","attachments")
                    getAttachments(logpath,discordlogs+"avatars/","avatars")


def buildAllAttachments(overallfolderpath,username,servername,channelname):
    discordlogs=overallfolderpath+"discordlogs/"+username+"/"+servername+"/"+channelname+"/"
#    print 'd:',discordlogs
    filelist = driveutils.readDir(discordlogs)
    filelist.sort()
    for timefile in filelist:
        if os.path.isfile(discordlogs+timefile) and re.match("^\d{4}_\d{2}_\d{2}\.html\s*$",timefile):
            timefolder=re.sub("_","",timefile)
            timefolder=re.findall("^(\d+)",timefolder).pop()
            getAttachments(discordlogs+timefile,discordlogs+"attachments/"+timefolder+"/","attachments")
            getAttachments(discordlogs+timefile,discordlogs+"avatars/","avatars")


def getAttachments(filename,folderpath,dltype="attachments"):
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

#    print '-dl:',filename
    with open(filename) as f:
        for rline in f.readlines():
            rline=rline.rstrip()

            matchreg=".*=\s*\"https\:\/\/cdn\.discordapp\.com\/"+dltype+"\/[\/\.\w\-]+[\"']"
            if re.match(matchreg,rline):
                findreg1="[\"'](https\:\/\/cdn\.discordapp\.com\/"+dltype+"\/[\/\.\w\-]+)[\"']"
                url=re.findall(findreg1,rline)[0]
                if url is not None:
                    findregstart="[\"']https\:\/\/cdn\.discordapp\.com\/"+dltype
                    findreg2=re.compile(findregstart+"(\/[\/\.\w\\\-]+[\\\/])[\.\w\-]+[\"']")
                    findreg3=re.compile(findregstart+"\/[\/\.\w\\\-]+[\\\/]([\.\w\-]+)[\"']")
                    urlfolder=re.findall(findreg2,rline)[0]
                    urlfile=re.findall(findreg3,rline)[0]

                    if not os.path.exists(folderpath+urlfolder):
                        os.makedirs(folderpath+urlfolder)
                    if not os.path.exists(folderpath+urlfolder+urlfile):

#                        context = ssl._create_unverified_context()
#                        urllib.urlopen(url, context=context)

#                        urllib.urlretrieve(url, folderpath+urlfolder+urlfile)
#                        print ' - - attachment:',folderpath+urlfolder+urlfile
                        print " - - url:",url
                        req = urllib2.Request(url, headers={ 'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXX' })
                        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11");

                        try:
                            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
                            res = urllib2.urlopen(req, context=gcontext)
                            info = res.read()
                        except urllib2.HTTPError as exception:
                            print '*****ERRR*****',exception
                            print url
                            print folderpath+urlfolder+urlfile
                            print '  **********',exception
                            continue

                        attachmentfile = open(folderpath+urlfolder+urlfile, 'w')
                        attachmentfile.write(info)
                        attachmentfile.close()

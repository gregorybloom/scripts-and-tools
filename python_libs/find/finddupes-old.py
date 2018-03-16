
import os, sys, hashlib, time, re
from maintenance_loader import *



logfolder = "logs"

hashes = {}
groups = {}
gd=0

log1=''
log2=''

def findDupes(logA, logB, logname, groupby="sha"):
        global log1,log2
        log1 = logA
        log2 = logB

	driveutils.createNewLog(logfolder+'/'+ logname)
	beginWalkCompare(logA, logB, logname, groupby)



def beginWalkCompare(logA, logB, logname, groupby="sha"):
	global hashes
        global groups
	global gd

	hashes = {}
	gd=0

	logAf = open(logA, 'rb')
	while 1:
		line = logAf.readline()
		if not line:
			break

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if re.search(reg,line):
			objA = driveutils.decomposeFileLog(line,1)


                        hash = findgroup(objA)

			if hashes.has_key( hash ):
				print '/x ' + objA['fulltext'].strip()
				continue
			if (gd%10)==0:
				print '/ ' + objA['fulltext'].strip()
			hashes[hash] = 0

			if not preWalkCompare(objA, logB, groupby):
                            continue

                        if not groups.has_key( hash ):
                                groups[hash] = {}
                        hashes[hash] = 1

			if(logA != logB):
                            walkCompare(objA, logA, logname, groupby)
			count = walkCompare(objA, logB, logname, groupby)

def buildLogName(logname,otherlog):
	div = logname.find('/')
	if div >= 0:
		parts = logname.rsplit('/',2)
		path = parts[0]
	else:
		path=""
	div = otherlog.find('/')
	if div >= 0:
		parts = logname.rsplit('/',2)
		logname = parts[1]

	logname = path +'/'+ logname
	return logname

def preWalkCompare(objA, logB, groupby):
	global hashes

	logB2f = open(logB, 'rb')

	while 1:
		line2 = logB2f.readline()
		if not line2:
			break

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if re.search(reg,line2):
			objB2 = driveutils.decomposeFileLog(line2,1)

                        grID = comparegroup(objA, objB2, groupby)
                        if grID != False:
                            return True
	return False



def walkCompare(objA, logB, logname, groupby):
        global log1,log2
	global hashes
	global gd

	c=0
	logBf = open(logB, 'rb')
	while 1:
		line2 = logBf.readline()
		if not line2:
			break

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if re.search(reg,line2):
			objB = driveutils.decomposeFileLog(line2,1)

                        if log1==log2:
                                if objA['fullpath']==objB['fullpath']:
                                    driveutils.addToLog("// "+objB['fulltext'], logfolder+'/'+ logname)
                                    if (gd%10)==0:
                                            print '- ' + objB['fulltext'].strip()
                                    gd=gd+1
                                    continue

                        grID = comparegroup(objA, objB, groupby)
                        if grID != False:

                            if logB==log1 and log1!=log2:
                                    driveutils.addToLog("// "+objB['fulltext'], logfolder+'/'+ logname)
                                    if (gd%10)==0:
                                            print '- ' + objB['fulltext'].strip()
                            elif logB==log2:
                                    driveutils.addToLog(objB['fulltext'], logfolder+'/'+ logname)
                                    if (gd%10)==0:
                                            print '* ' + objB['fulltext'].strip()

                            c=c+1
                            gd=gd+1
	return c




def findgroup(obj, groupby="sha"):
        if(groupby == "sha"):
            return obj['sha']

        elif(groupby == "data"):
            if obj['sha'] == "**********":
                return False
            if obj['bytesize'] < 0:
                return False

            if(  not os.path.exists("tmp/tmp4")  ):
                os.makedirs("tmp/tmp4")
            shutil.copy( obj['fullpath'], "tmp/tmp1/file."+objA['filetype'] );
            objA = log_utils.getFileInfo( "tmp/tmp1/file."+objA['filetype'] )
            try:
                    shutil.rmtree("tmp/")
            except OSError as exception:
                    print '** err on '+str(exception)
            return objA['sha']



def comparegroup(objA, objB, groupby="sha"):
        if(objA['fullpath'] == objB['fullpath']):
            return False

        if(groupby == "sha"):
            if (objA['sha'] != objB['sha']):
                return False
            if objA['bytesize'] != objB['bytesize']:
                return False
            return objA['sha']

        elif(groupby == "data"):

            if objA['bytesize'] != objB['bytesize']:
                return False
            if objA['filetype'] != objB['filetype']:
                return False
            if objA['sha'] == "**********" or objB['sha'] == "**********":
                return False
            if objA['bytesize'] < 0 or objB['bytesize'] < 0:
                return False


            if(  not os.path.exists("tmp/tmp1")  ):
                os.makedirs("tmp/tmp1")
	    if(  not os.path.exists("tmp/tmp2")  ):
	            os.makedirs("tmp/tmp2")

            shutil.copy( objA['fullpath'], "tmp/tmp1/file."+objA['filetype'] );
            shutil.copy( objB['fullpath'], "tmp/tmp2/file."+objB['filetype'] );

            objA1 = log_utils.getFileInfo( "tmp/tmp1/file."+objA['filetype'] )
            objB1 = log_utils.getFileInfo( "tmp/tmp2/file."+objB['filetype'] )

            try:
                    shutil.rmtree("tmp/")
            except OSError as exception:
                    print '** err on '+str(exception)

            if(  objA1['sha'] == objB1['sha']  ):
                return objA1['sha']

        return False





#scanForLog(ComputerLog, PassportLog, "PassportCompare.txt")
#scanForLog(ComputerAkagiLog, BlackPassportAkagiLog, "BlackPassportAkagiCompare.txt")

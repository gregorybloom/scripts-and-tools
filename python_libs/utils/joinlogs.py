
import os, sys, hashlib, time, re
from maintenance_loader import *



logfolder = "logs"


def beginSplitJoin(splitfolder, joinedlog):
	driveutils.createNewLog(logfolder+'/'+ joinedlog)
	gatherSplits(splitfolder, joinedlog)


def gatherSplits(splitfolder, joinedlog):
	files = driveutils.readDir(splitfolder)
	for file in files:
		
		namestr = str(file)
		fname = splitfolder+'/'+namestr

		if(  not os.path.isdir(fname)  ):

			regtxt = r'log.txt$'	
			if re.search(regtxt,fname):

				print '- '+namestr
				appendSplit(fname, joinedlog)
				
def appendSplit(splitname, joinedlog):
	logA = open(splitname, 'rb')
	while 1:
		line = logA.readline()
		if not line:
			break

		driveutils.addToLog(line, logfolder+'/'+ joinedlog)




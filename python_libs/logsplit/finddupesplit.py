
import os, sys, hashlib, time, re
from maintenance_loader import *


logfolder = "logs"

def beginSplitOwnCompare(folderA, comparefolder,skipto=1):
	logFirstOwnSplit(folderA, comparefolder,skipto)
	



def logFirstOwnSplit(folderA, comparefolder,skipto=1):
	c=0
	files = driveutils.readDir(folderA)
	for file in files:
		
		namestr = str(file)
		fname = folderA+'/'+namestr

		if(  not os.path.isdir(fname)  ):

			regtxt = r'log.txt$'	
			if re.search(regtxt,fname):
				
				if c<(skipto-1):
					c=c+1
					continue
				
				logSecondOwnSplit(namestr, folderA, comparefolder)
				c=c+1


def logSecondOwnSplit(fileA, folderA, comparefolder):
	
	files = driveutils.readDir(folderA)
	for file in files:
		
		namestr = str(file)
		fname = folderA+'/'+namestr

		if(  not os.path.isdir(fname)  ):

			regtxt = r'log.txt$'	
			if re.search(regtxt,fname):
				
				fileB = namestr
				if fileB == fileA:
				
					fPathA = folderA+'/'+fileA
					fLog = comparefolder+'/'+fileA
				
					print fPathA +"      "+ fLog

					driveutils.createNewLog(logfolder+'/'+comparefolder+'/'+ fileA)
					findowndupes.findOwnDupes(fPathA, fLog)
					




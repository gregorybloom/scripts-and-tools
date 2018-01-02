
import os, sys, hashlib, time, re
from maintenance_loader import *


logfolder = "logs"

def beginSplitCompare(folderA, folderB, comparefolder,skipto=1):
	logFirstSplit(folderA, folderB, comparefolder,skipto)
	



def logFirstSplit(folderA, folderB, comparefolder,skipto=1):
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
				
				logSecondSplit(namestr, folderA, folderB, comparefolder)
				c=c+1


def logSecondSplit(fileA, folderA, folderB, comparefolder):
	
	files = driveutils.readDir(folderB)
	for file in files:
		
		namestr = str(file)
		fname = folderB+'/'+namestr

		if(  not os.path.isdir(fname)  ):

			regtxt = r'log.txt$'	
			if re.search(regtxt,fname):
				
				fileB = namestr
				if fileB == fileA:
				
					fPathA = folderA+'/'+fileA
					fPathB = folderB+'/'+fileB
					fLog = comparefolder+'/'+fileA
				
					print fPathA +"  "+ fPathB +"      "+ fLog

					driveutils.createNewLog(logfolder+'/'+comparefolder+'/'+ fileA)
					finddupes.findDupes(fPathA, fPathB, fLog)
					




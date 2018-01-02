
import os, sys, hashlib, time, re
from maintenance_loader import *


PassportLog = "logs/PassportFolderLog.txt"
ComputerLog = "logs/ComputerFolderLog.txt"

PassportDrive = "/Volumes/My Passport"
ComputerDrive = "/Users/greg"

sessionlog = "logs"

compiledlog = []










def scanForLog(base, path, logname):
	driveutils.createNewLog(sessionlog+'/'+ logname)
	spiderFiles(base, path, logname)


def spiderFiles(base, path, logname):
	
	files = driveutils.readDir(base+"/"+path)

	for file in files:
		
		namestr = str(file)
		fname = base+"/"+path+namestr
		
		if(  os.path.isdir(fname)  ):
			logFolderContents(fname+"/", logname)
			spiderFiles(base,path+namestr+"/",logname)


def logFolderContents( fullpath, log ):
		
	f=0
	c=0
	files = driveutils.readDir(fullpath)
	for file in files:
		if(  os.path.isdir(fullpath+file)  ):
			f=f+1
		else:
			c=c+1
	
	textout = fullpath +", "+ str(c) +" files, "+ str(f) +" folders"
	print textout
	
	fo = open( sessionlog +"/"+ log, 'ab' )
	fo.write( textout+'\n' )
	fo.close()


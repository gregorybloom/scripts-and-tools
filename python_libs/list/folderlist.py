
import os, sys, hashlib, time
from maintenance_loader import *


logfolder = "logs"

compiledlog = []


def beginFolderList(base, logname):
	driveutils.createNewLog(logfolder+'/'+ logname)
	spiderFiles(base, "", logname)


def spiderFiles(base, path, logname):
	
	files = driveutils.readDir(base+"/"+path)

	for file in files:
		
		namestr = str(file)
		fname = base+"/"+path+namestr


		
		if(  os.path.isdir(fname)  ):
			if( path=="" ) and (str(file)==".Trashes"):
				continue

			logFolderContents(fname+"/", logname)
			spiderFiles(base,path+namestr+"/",logname)


def logFolderContents( fullpath, log ):
		
	f=0
	c=0
	try:
		files = driveutils.readDir(fullpath)
	except OSError as exception:
		raise
		files = []
	for file in files:
		if(  os.path.isdir(fullpath+file)  ):
			f=f+1
		else:
			c=c+1
	
	textout = fullpath +", "+ str(c) +" files, "+ str(f) +" folders"
	print textout
	
	fo = open( logfolder +"/"+ log, 'ab' )
	fo.write( textout+'\n' )
	fo.close()
    





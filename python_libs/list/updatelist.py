from maintenance_loader import *

import os, sys, hashlib, time, re

import subprocess
from subprocess import *

from Queue import Queue
from threading import Thread


ix = 0
gc = 0


def beginMD5UpdateWalk(path,logname,newtype,walkopts=None):
	global gc
	gc=0
	if walkopts is None:
		walkopts={}

	namefilters=None
	if 'filters' in walkopts.keys():
		namefilters=walkopts['filters']

	driveutils.createNewLog(logname,False)
	for folder,subs,files in os.walk(basepath):
		for filename in files:

			fullpath=os.path.join(folder,filename)
			folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
			if (namefilters is None) or (not driveutils.ignoreFile(filename,folderpath,fullpath,namefilters)):
#				basepath = re.findall(r'^(.*\/)[^\/]+$',fullpath)[0]
#				namestr = re.findall(r'^.*\/([^\/]+\S)\s*$',fullpath)[0]

				count=None
				if 'useblocks' in walkopts.keys() and '_count' in walkopts['useblocks'].keys():
					count=int(walkopts['useblocks']['_count'])
				obj = driveutils.getFileInfo( fullpath, count, walkopts )
				newobj = comparefns.redoDataFile(obj['fulltext'],logsetname,filename,basepath,walkopts)
				fo = open( logname, 'ab' )
				fo.write( newobj['fulltext']+'\n' )
				fo.close()

		for foldern in folder:
			md5UpdateWalk(basepath,foldern,logname,newtype,walkopts)


def md5UpdateWalk(basepath,relativepath,logname,newtype,walkopts=None):
	global ix
	global gc
	if walkopts is None:
		walkopts={}

#	print '.',logname,walkopts
	folderslist=[]
	try:
		fileslist = driveutils.readDir(basepath+"/"+relativepath)
	except OSError as exception:
		if '_errs' not in walkopts.keys():
			walkopts['_errs']={}
		if '_folders' not in walkopts['_errs'].keys():
			walkopts['_errs']['_folders']=[]
		walkopts['_errs']['_folders'].append(basepath+"/"+relativepath)
		return

	fileslist.sort()

	if ix > 10000:
		print ix,' v '+basepath+'/'+relativepath
	for filen in fileslist:
		namestr = str(filen)
		pathTo = basepath+"/"+relativepath+'/'+namestr

		filters=None
#		if namestr == "New Monsters Aarakocra to Devil.doc":
#			print '       ',filen, walkopts.keys(), walkopts
		if 'filters' in walkopts.keys():
			filters=walkopts['filters']

		if(driveutils.ignoreFile(namestr,relativepath,pathTo,filters)):
#			filew = open("/logs/test/skipped.txt", "a")
#			filew.write(pathTo+"\n")
#			filew.close()
			continue

		if( not os.path.isdir(pathTo) ):
			logged=False
			if 'skipto' in walkopts.keys():
				if ( gc >= walkopts['skipto'] ):
					logged=True
			else:
				logged=True

			if logged:
				if 'printon' in walkopts.keys():
					if (ix % walkopts['printon'])==0:
						print walkopts['printon'],' logged '+pathTo

#				count=None
#				if 'useblocks' in walkopts.keys() and '_count' in walkopts['useblocks'].keys():
#					count=int(walkopts['useblocks']['_count'])
#				obj = driveutils.getFileInfo( fullpath, count, walkopts )
#				newobj = comparefns.redoDataFile(obj['fulltext'],logsetname,filename,basepath,walkopts)
#				fo = open( logname, 'ab' )
#				fo.write( obj['fulltext']+'\n' )
#				fo.close()

				driveutils.logThisFile( basepath+relativepath+'/', namestr, logname, walkopts )
				if 'printon' in walkopts.keys():
					ix = ix+1
#				else:
#					print 'logged '+pathTo
			gc = gc+1
		else:
			folderslist.append(namestr)
	for foldern in folderslist:
		md5UpdateWalk(basepath,relativepath+"/"+foldern,logname,newtype,walkopts)

from maintenance_loader import *

import os, sys, hashlib, time, re

import subprocess
from subprocess import *

from Queue import Queue
from threading import Thread


ix = 0
gc = 0


def beginMD5Walk(dirpath,logname,walkopts=None):

	global gc
	gc=0
	if walkopts is None:
		walkopts={}

	namefilters=None
	if 'filters' in walkopts.keys():
		namefilters=walkopts['filters']

	driveutils.createNewLog(logname,False)

	if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
		print '- .start',dirpath

	if 'walkmode' not in walkopts.keys():
		md5Walk(dirpath,'',logname,walkopts)
	else:
		walkMD5Fast( dirpath, logname, walkopts )

	if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
		print '- .end',dirpath

def md5Walk(base,path,logname,walkopts=None):
	global ix
	global gc
	if walkopts is None:
		walkopts={}

	if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
		print '- . . read',base,',',"/"+path

	folderslist=[]
	try:
		fileslist = driveutils.readDir(base+"/"+path)
	except OSError as exception:
		if '_errs' not in walkopts.keys():
			walkopts['_errs']={}
		if '_folders' not in walkopts['_errs'].keys():
			walkopts['_errs']['_folders']=[]
		walkopts['_errs']['_folders'].append(base+"/"+path)
		return

	fileslist.sort()

	if ix > 10000:
		print ix,' v '+base+'/'+path
	for filen in fileslist:
		namestr = str(filen)
		pathTo = base+"/"+path+'/'+namestr

		filters=None
#		if namestr == "New Monsters Aarakocra to Devil.doc":
#			print '       ',filen, walkopts.keys(), walkopts
		if 'filters' in walkopts.keys():
			filters=walkopts['filters']

		if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
			print '- . . . check',base,',',"/"+path,',',pathTo
		if(driveutils.ignoreFile(namestr,path,pathTo,filters)):
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

				if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
					print '- . . . check',base,',',"/"+path,',',pathTo

				if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
					print '- . . . log start',base,',',"/"+path,',',pathTo
				driveutils.logThisFile( base+path+'/', namestr, logname, walkopts )
				if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
					print '- . . . log end',base,',',"/"+path,',',pathTo


				if 'printon' in walkopts.keys():
					ix = ix+1
#				else:
#					print 'logged '+pathTo
			gc = gc+1
		else:
			folderslist.append(namestr)
	for foldern in folderslist:
		if 'verbose' in walkopts.keys() and walkopts['verbose'] == True:
			print '- . . . next',base,',',"/"+path,',',foldern
		md5Walk(base,path+"/"+foldern,logname,walkopts)

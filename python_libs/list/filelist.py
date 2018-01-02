from maintenance_loader import *

import os, sys, hashlib, time



ix = 0
gc = 0


def beginMD5Walk(path,logname,walkopts=None):
	global gc
	gc=0
	if walkopts is None:
		walkopts={}
	if os.path.isfile("/logs/test/skipped.txt"):
		os.remove("/logs/test/skipped.txt")

#	print '--------',walkopts
	driveutils.createNewLog(logname,False)
	md5Walk(path,'',logname,walkopts)

def md5Walk(base,path,logname,walkopts=None):
	global ix
	global gc
	if walkopts is None:
		walkopts={}

#	print '.',logname,walkopts
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

#	print ' v '+base+'/'+path
	for filen in fileslist:
		namestr = str(filen)
		pathTo = base+"/"+path+'/'+namestr

		filters=None
#		if namestr == "New Monsters Aarakocra to Devil.doc":
#			print '       ',filen, walkopts.keys(), walkopts
		if 'filters' in walkopts.keys():
			filters=walkopts['filters']

		if(driveutils.ignoreFile(namestr,path,pathTo,filters)):
			filew = open("/logs/test/skipped.txt", "a")
			filew.write(pathTo+"\n")
			filew.close()
			continue

		if( not os.path.isdir(pathTo) ):
			logged=False
			if 'skipto' in walkopts.keys():
				if ( gc >= walkopts['skipto'] ):
					logged=True
			else:
				logged=True

			if logged:
				driveutils.logThisFile( base+"/"+path+'/', namestr, logname )
				if 'printon' in walkopts.keys():
					ix = ix+1
#					if (ix % walkopts['printon'])==0:
#						print 'logged '+pathTo
#				else:
#					print 'logged '+pathTo
			gc = gc+1
		else:
			folderslist.append(namestr)
	for foldern in folderslist:
		md5Walk(base,path+"/"+foldern,logname,walkopts)

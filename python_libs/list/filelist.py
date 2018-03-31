from maintenance_loader import *

import os, sys, hashlib, time, re

import subprocess
from subprocess import *

from Queue import Queue
from threading import Thread


ix = 0
gc = 0


def beginMD5Walk(path,logname,walkopts=None):
	def md5er(q,type,log,dir,walkopts,filters=None):
		while True:
			fname=q.get()
			if fname is None:
				break
			if type=='normlog':
				basepath = re.findall(r'^(.*\/)[^\/]+$',fname)[0]
				namestr = re.findall(r'^.*\/([^\/]+\S)\s*$',fname)[0]
				driveutils.logThisFile( basepath, namestr, logname, walkopts )
			elif type=='subproc':
				proc = subprocess.Popen(["/usr/bin/sigtool", "--md5", fname],stdout=subprocess.PIPE)
				(out, err) = proc.communicate()
				logfile = open(log, "a+", -1)
				logfile.write(', '.join(out.split(':')[0:2])+', x, '+fname+"\n")
				logfile.close()
				proc.wait()
			q.task_done()

	global gc
	gc=0
	if walkopts is None:
		walkopts={}

	namefilters=None
	if 'filters' in walkopts.keys():
		namefilters=walkopts['filters']

	driveutils.createNewLog(logname,False)
	if 'threadprocess' in walkopts.keys():

		num_threads=2
		if 'numthreads' in walkopts.keys():
			num_threads=walkopts['numthreads']

		filequeue=Queue()
		threads=[]


		for i in range(num_threads):
			worker = Thread(target=md5er, args=(filequeue,'normlog',logname,path,walkopts,namefilters))
			worker.setDaemon(True)
			threads.append(worker)
			worker.start()

		for folder,subs,files in os.walk(path):
			for filename in files:

				fullpath=os.path.join(folder,filename)
				folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
				if (namefilters is None) or (not driveutils.ignoreFile(filename,folderpath,fullpath,namefilters)):
					filequeue.put(fullpath)
		filequeue.join()

		for i in range(num_threads):
		    filequeue.put(None)
		for t in threads:
			t.join()

	elif 'quickprocess' in walkopts.keys():
		for folder,subs,files in os.walk(path):
			for filename in files:

				fullpath=os.path.join(folder,filename)
				folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
				if (namefilters is None) or (not driveutils.ignoreFile(filename,folderpath,fullpath,namefilters)):
					basepath = re.findall(r'^(.*\/)[^\/]+$',fullpath)[0]
					namestr = re.findall(r'^.*\/([^\/]+\S)\s*$',fullpath)[0]
					driveutils.logThisFile( basepath, namestr, logname, walkopts )

	elif 'sigprocess' in walkopts.keys():
		for folder,subs,files in os.walk(path):
			for filename in files:

				fullpath=os.path.join(folder,filename)
				folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
				if (namefilters is None) or (not driveutils.ignoreFile(filename,folderpath,fullpath,namefilters)):
					basepath = re.findall(r'^(.*\/)[^\/]+$',fullpath)[0]
					namestr = re.findall(r'^.*\/([^\/]+\S)\s*$',fullpath)[0]

					proc = subprocess.Popen(["/usr/bin/sigtool", "--md5", fullpath],stdout=subprocess.PIPE)
					(out, err) = proc.communicate()
					logfile = open(logname, "a+", -1)
					logfile.write(', '.join(out.split(':')[0:2])+', x, '+fullpath+"\n")
					logfile.close()
					proc.wait()

	else:
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
				driveutils.logThisFile( base+path+'/', namestr, logname, walkopts )
				if 'printon' in walkopts.keys():
					ix = ix+1
#				else:
#					print 'logged '+pathTo
			gc = gc+1
		else:
			folderslist.append(namestr)
	for foldern in folderslist:
		md5Walk(base,path+"/"+foldern,logname,walkopts)

from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv, datetime
import mmh3

import subprocess
from subprocess import *
from Queue import Queue
from threading import Thread


def pythonExamineFile( filepath, opts ):
	c=1
	if 'count' in opts.keys():
		c=opts['count']
	mtype='md5'
	if 'mtype' in opts.keys():
		mtype=opts['mtype']
	sum=shaSum(filepath,c,mtype)
	fsize=getSize(filepath)
	outstr=str(sum)+', '+str(fsize)+', mtype:'+mtype+', x, '+filepath.rstrip()
	return outstr

def pythonWalk( dirpath, targetlog, opts ):
	namefilters=None
	if 'filters' in opts.keys():
		namefilters=opts['filters']
	driveutils.createNewLog(targetlog,True)
	outlog = open(targetlog, 'ab')
	for folder,subs,files in os.walk(dirpath):
		for filename in files:
			fullpath=os.path.join(folder,filename)
			folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
			if (namefilters is None) or (not driveutils.ignoreFile(filename,folderpath,fullpath,namefilters)):
				c=1
				if 'count' in opts.keys():
					c=opts['count']
				mtype='md5'
				if 'mtype' in opts.keys():
					mtype=opts['mtype']
				sum=shaSum(fullpath,c,mtype)
				fsize=getSize(fullpath)
				outstr=str(sum)+', '+str(fsize)+', mtype:'+mtype+', x, '+fullpath.rstrip()
				outlog.write(outstr+'\n')
	outlog.close()
def testMD5Fast( dirpath, targetlog, opts ):
#	https://stackoverflow.com/questions/33152171/why-does-multiprocessing-process-join-hang
	def md5er(q,log,dir,opts,filters=None):
		while True:
			fname=q.get()
			if fname is None:
				break
			mtype='md5'
			if 'mtype' in opts.keys():
				mtype=opts['mtype']

			proc = subprocess.Popen(["/usr/bin/sigtool", "--md5", fname],stdout=subprocess.PIPE)
			(out, err) = proc.communicate()
			logfile = open(log, "a+", -1)
			logfile.write(', '.join(out.split(':')[0:2])+', mtype:'+mtype+', x, '+fname+"\n")
			logfile.close()
			proc.wait()
			q.task_done()
	num_threads=2
	if 'numthreads' in opts.keys():
		num_threads=opts['numthreads']

	filequeue=Queue()
	threads=[]

	namefilters=None
	if 'filters' in opts.keys():
		namefilters=opts['filters']

	for i in range(num_threads):
		worker = Thread(target=md5er, args=(filequeue,targetlog,dirpath,opts,namefilters))
		worker.setDaemon(True)
		threads.append(worker)
		worker.start()

	for folder,subs,files in os.walk(dirpath):
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


def file_len(fname):
	i=0
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return (i + 1)

def shaSum(filename,count=1,style="md5"):
	if style == "md5":
		sha = hashlib.md5()
	if style == "sha1":
		sha = hashlib.sha1()
	if style == "sha256":
		sha = hashlib.sha256()
#	mmh3.hash_from_buffer(numpy.random.rand(100), signed = False)
#	if style == "mmh3":
#		sha = mmh3.hash128('foo', 42, True)
	with open(filename, 'rb') as f:
		for chunk in iter(lambda: f.read(count * 128 * sha.block_size), b''):
			sha.update(chunk)
	return sha.hexdigest()
def getSize(filename):
	sizeSt = -1
	try:
		sizeSt = os.path.getsize(filename)
	except OSError as exception:
		sizeSt = -1
	return sizeSt



def useMethod(method, path, targetlog, opts):
	if os.path.exists(targetlog):
		os.remove(targetlog)
	if method == "python_walk":
		#normal walkpath
		filelist.beginMD5Walk(path,targetlog,opts)
	if method == "sigtool_walk":
		# uses thread/queeing with sigtool
		testMD5Fast(path,targetlog,opts)
	if method == "sigtool_walk4":
		# uses thread/queeing with sigtool
		opts['numthreads']=4
		testMD5Fast(path,targetlog,opts)
		del opts['numthreads']
	if method == "python_thread":
		# uses threading/queuing with python 'log this file'
#		opts['threadprocess']=True
		opts['walkmode']='threadprocess'
		filelist.beginMD5Walk(path,targetlog,opts)
#		del opts['threadprocess']
	if method == "python_thread4":
		# uses threading/queuing with python 'log this file'
		opts['numthreads']=4
#		opts['threadprocess']=True
		opts['walkmode']='threadprocess'
		filelist.beginMD5Walk(path,targetlog,opts)
#		del opts['threadprocess']
		del opts['numthreads']
	if method == "python_quick":
		# uses straight python 'log this file'
#		opts['quickprocess']=True
		opts['walkmode']='quickprocess'
		filelist.beginMD5Walk(path,targetlog,opts)
#		del opts['quickprocess']
	if method == "sigtool_quick":
		# uses subprocess sigtool with no queue/threading
#		opts['sigprocess']=True
		opts['walkmode']='sigprocess'
		filelist.beginMD5Walk(path,targetlog,opts)
#		del opts['sigprocess']
	if method == "py_walkX":
		opts['count']=1
		pythonWalk(path,targetlog,opts)
	if method == "py_walkX4":
		opts['count']=4
		pythonWalk(path,targetlog,opts)
	if method == "py_walkX8":
		opts['count']=8
		pythonWalk(path,targetlog,opts)
	if method == "py_walkX16":
		opts['count']=16
		pythonWalk(path,targetlog,opts)
	if method == "py_walkX32":
		opts['count']=32
		pythonWalk(path,targetlog,opts)
	if method == "py_walkX64":
		opts['count']=64
		pythonWalk(path,targetlog,opts)
	if method == "py_walkX128":
		opts['count']=128
		pythonWalk(path,targetlog,opts)
	if method == "py_walkX256":
		opts['count']=256
		pythonWalk(path,targetlog,opts)

	if os.path.exists(targetlog):
		return file_len(targetlog)
	return -1



opts={}
opts['filters']={'deny':["garbage"],'allowonly':["imgs","videos","docs","zip","music","misc"]}


targetList={}
targetList['cloudset']='/media/raid/CLOUD_BACKUP'
targetList['dataset']='/media/raid/Data'
targetList['miscset']='/media/raid/Misc'
targetList['projset']='/media/raid/Projects'
targetList['servscriptset']='/media/raid/SERVER_SCRIPTS'
targetList['sidedriveset']='/media/raid/SIDE_DRIVES'
targetList['softset']='/media/raid/Software'
targetList['spiderdumpset']='/media/raid/SPIDER_DUMP'
targetList['m_bookset']='/media/raid/Media/Books'
targetList['m_comicset']='/media/raid/Media/Comics'
targetList['m_imageset']='/media/raid/Media/Images'
targetList['m_musicset']='/media/raid/Media/Music'
targetList['m_recordingset']='/media/raid/Media/Recordings'
targetList['m_unsortedset']='/media/raid/Media/-unsorted'

doList = ['dataset', 'miscset', 'projset', 'servscriptset', 'softset', 'spiderdumpset', 'm_bookset', 'm_imageset', 'm_musicset', 'm_recordingset', 'm_unsortedset']

doList = ['m_bookset', 'dataset', 'miscset', 'projset', 'servscriptset', 'softset', 'spiderdumpset', 'm_imageset', 'm_musicset', 'm_recordingset', 'm_unsortedset']


apath="/media/raid/testpath/"
logname="/tmp/thefuck.txt"



countlist=[64,96,128,160,192,224,256,288,320,352,384,416,448,480,512,576,640,704,768,832,916,1010]
filelist=[]
#filelist.append( "/media/raid/Media/Videos/Other/Misc Movies/Antichamber Launch Trailer - January 31st, 2013 on Steam.mp4" )
#filelist.append( "/media/raid/Media/Videos/Anime/-unfinished/[HorribleSubs] 3-gatsu no Lion - 22 [1080p].mkv" )
#filelist.append( "/media/raid/Media/Videos/Anime/-unfinished/[HorribleSubs] JoJo's Bizarre Adventure - Diamond is Unbreakable - 13 [1080p].mkv" )

driveutils.createNewLog(logname,True)
outlog = open(logname, 'ab')
for file in filelist:
	break
	###################################
	for c in countlist:
		start=datetime.datetime.now()
		textstr=pythonExamineFile(file,{'count':c})
		end=datetime.datetime.now()
		outlog.write(textstr+"\n")
		print c,(end-start),file
#		print textstr
outlog.close()
#sys.exit(0)


countlist=[64,96,128,160,192,224,256,288,320,352]
countlist=[16,32,64,96,128,160,192,224,256,288,320,352]
countlist=[16,32,64,96,128,160,192,224]
countlist=[64,96,128,160,192]
folderlist=[]
#folderlist.append( "/media/raid/CLOUD_BACKUP/" )
#folderlist.append( "/media/raid/Data/" )
#folderlist.append( "/media/raid/Misc/" )
#folderlist.append( "/media/raid/Projects/" )
#folderlist.append( "/media/raid/SERVER_SCRIPTS/" )
folderlist.append( "/media/raid/Software/" )
folderlist.append( "/media/raid/Media/Books/" )
#folderlist.append( "/media/raid/Media/Comics/" )
folderlist.append( "/media/raid/Media/Images/" )
folderlist.append( "/media/raid/Media/Music/" )
#folderlist.append( "/media/raid/Media/Recordings/" )
#folderlist.append( "/media/raid/Media/-unsorted/" )
#folderlist.append( "/media/raid/SIDE_DRIVES/" )
#folderlist.append( "/media/raid/Media/Videos/" )

folderlist.append( "/media/raid/Media/Videos/Anime/-unfinished/Boku no Hero Academia/" )
#folderlist.append( "/media/raid/Media/Videos/Other/Misc Movies/" )
#folderlist.append( "/media/raid/Media/Videos/Anime/-unfinished/Trinity Seven[DameDesuYo]/" )
#mtypearr=["md5","sha1"]
mtypearr=["sha1"]
for mtype in mtypearr:
	for folder in folderlist:
		for c in countlist:
			start=datetime.datetime.now()
			opts['count']=c
			opts['mtype']=mtype
			pythonWalk(folder,logname,opts)
			end=datetime.datetime.now()
			print mtype,c,(end-start),folder
#		print textstr

sys.exit(0)
#############################################################################################################


timeset={}

patharr=[]
for doitem in doList:
    if doitem in targetList.keys():
        patharr.append( {'name':doitem,'path':targetList[doitem]} )

c=0

methodarr=['python_walk','py_walkX','py_walkX4','py_walkX8','py_walkX16','py_walkX32', 'sigtool_quick', 'python_quick', 'sigtool_walk', 'sigtool_walk4', 'python_thread', 'python_thread4']
methodarr=['py_walkX256', 'py_walkX128','py_walkX64', 'py_walkX32', 'python_walk','sigtool_walk4', 'python_thread4']		#	'python_quick',
#methodarr=['sigtool_folder']
for pathobj in patharr:
	path = pathobj['path']
	pathname = pathobj['name']

	print c,pathname,path

	c2=0
	for method in methodarr:
		timeset[c]={}
		timeset[c][method]={}
		timeset[c][method]['start']=datetime.datetime.now()
		lcount= useMethod(method, path, logname+'.'+str(c)+"."+str(c2), opts)
		timeset[c][method]['end']=datetime.datetime.now()
		timeset[c][method]['path']=path
		print 'finished: \t',pathname,method,' \t -hits:',lcount,' - \t\t',(timeset[c][method]['end']-timeset[c][method]['start'])
		c2+=1
	c+=1


for step,tmset in timeset.iteritems():
    for walk,tset in timeset[step].iteritems():
        print c, walk, str(tset['end']-tset['start']), tset['path']
    print '-------------'


import io, os, sys, hashlib, time, re
import csv
import copy
import subprocess
from subprocess import *
#from Queue import Queue
try:
   import queue
except ImportError:
   import Queue as queue
from threading import Thread



filterlist={}
filterlist['garbage']=["^\.[\~_].*","^\.DS_Store$","^\.localized$","^ICON$","^Icon$"]
filterlist['imgs']=[".*\.[jJ]pe?g$",".*\.JPE?G$",".*\.gif$",".*\.(?:png|PNG)$",".*\.tiff$",".*\.bmp$"]
filterlist['videos']=[".*\.mkv$",".*\.rm$",".*\.avi(?:\.\w{2,5})?$",".*\.mp4(?:\.\w{2,5})?$",".*\.ogm$",".*\.mov$",".*\.webm$"]
filterlist['docs']=[".*\.pdf$",".*\.epub$",".*\.mobi$",".*\.cb(?:z|r)$"]
filterlist['zip']=[".*\.zip$",".*\.tar(?:\.gz)?$",".*\.rar$"]
filterlist['music']=[".*\.mp3$",".*\.flac$",".*\.ogg$",".*\.wav$",".*\.m3u$",".*\.aiff$",".*\.wma$",".*\.aac$"]
filterlist['misc']=[".*\.torrent$"]


DEBUG_RUN = None
DEBUG_PATH = None
def addToDebugLog(useopts,text,debuglogpath=None):
	global DEBUG_RUN
	global DEBUG_PATH

	if 'debuglog' not in useopts.keys():
		return
	elif 'usedebug' not in useopts['debuglog'].keys() or useopts['debuglog']['usedebug'] < 1:
		return

	if DEBUG_RUN is None or DEBUG_PATH is None:
		if debuglogpath is not None:
			createNewLog(debuglogpath,True)
			DEBUG_PATH = debuglogpath
			DEBUG_RUN = True
			useopts['debuglog']['logpath'] = debuglogpath
		else:
			raise
	if DEBUG_PATH is not None:
		if 'showdebug' in useopts['debuglog'].keys() and useopts['debuglog']['showdebug'] > 0:
			print (text)
		addToLog( text+"\n", DEBUG_PATH )


def ignoreFile(namestr,path,fullpath,filters=None):
	if filters is None:
		filters={}
		filters['deny']=["garbage"]

	global filterlist

#	print '  :',namestr,path,fullpath

	if( os.path.islink(fullpath) ):
		return True
	if( path=="" ) and (namestr==".Trashes"):
		return True

	ftypes=['deny','allowonly']
	if 'deny' in filters.keys():
		for listname in filters['deny']:
			if listname in filterlist.keys():
				for filterstr in filterlist[listname]:
					if re.match(filterstr,namestr,re.IGNORECASE):
						return True
	if( os.path.isdir(fullpath) ):
		return False
	if 'allowonly' in filters.keys():
		for listname in filters['allowonly']:
			if listname in filterlist.keys():
				for filterstr in filterlist[listname]:
					if re.match(filterstr,namestr,re.IGNORECASE):
#						print 't m',filterstr,namestr
						return False
		return True
	return False

def placeInDictSet(dictobj,buildarr,valueobj,buildinfo=[],d=0,act="replace"):
	buildarr2=copy.deepcopy(buildarr)
	if len(buildarr) == 0:
		return
	if d==0:
		createDictSet(dictobj,buildarr2,buildinfo)
	groupname = buildarr[0]
	buildarr.pop(0)
	if len(buildarr) > 0:
		placeInDictSet(dictobj[groupname],buildarr,valueobj,buildinfo,(d+1))
	else:
		if act == "increment":
			if isinstance(dictobj[groupname], dict):
				if valueobj['name'] not in dictobj[groupname].keys():
					dictobj[groupname][valueobj['name']]=0
				dictobj[groupname][valueobj['name']]+=valueobj['value']
			if isinstance(dictobj[groupname], int):
				dictobj[groupname]+=valueobj['value']
		if act == "replace" or act == "place":
			if isinstance(dictobj[groupname], dict):
				if act == "place" and valueobj['name'] in dictobj[groupname].keys():
					return
				dictobj[groupname][valueobj['name']]=valueobj['value']
			elif isinstance(dictobj[groupname], list):
				dictobj[groupname].append(valueobj)


def createDictSet(dictobj,buildarr,buildinfo=[]):
	if dictobj is None:
		dictobj={}
	if len(buildarr) == 0:
		return
	groupname = buildarr[0]
	if groupname not in dictobj.keys():
		if len(buildinfo) == 0 or buildinfo[0] == 'd':
			dictobj[groupname]={}
		elif buildinfo[0] == 'a':
			dictobj[groupname]=[]

	buildarr.pop(0)
	if len(buildinfo) > 0:
		buildinfo.pop(0)

	createDictSet(dictobj[groupname],buildarr,buildinfo)

def buildPath(*paths):
	def mapList(x):
		return x if not isinstance(x,list) else os.path.join(*x)
	pathstring=list(map(mapList,paths))
	return (os.path.join(*pathstring))


def createNewLog(logname, append=False):

	path = os.path.dirname(logname)
	if(  not os.path.exists(path)  ):
		try:
			print ('****** '+path)
			os.makedirs(path)
		except OSError as exception:
#			if exception.errno != errno.EEXIST:
			raise
#	print(logname)
#	print(path)
	if append:
		fo = open( logname, 'a' )
		fo.close()
	else:
		fo = open( logname, 'w' )
		fo.close()



def sortLogByPath(logpath,order=3):
	if os.path.exists(logpath+".sorttmp"):
		return
	writefile = open(logpath+'.sorttmp', 'wb')
	readfile = csv.reader(open(logpath), delimiter=",")
#	filteredRows = filter(lambda x: len(x) > order, readfile)
	filteredRows = filter(lambda x: (os.path.sep not in x, x), readfile)
	for line in sorted(filteredRows, key=lambda line: ','.join(line[order:])):
		strng=','.join(line)
		writefile.write(strng+'\n')
	writefile.close()

	os.remove(logpath)
	os.rename(logpath+".sorttmp",logpath)
#	print 'sorted: ',logpath


def rebuildFileLogItemData(logitemobj):
	parts=[]
	for name,item in logitemobj.iteritems():
		parts.append(name+":"+item)
	str = '|'.join(parts)
	return str

def decomposeFileLogItemData(logitemstr):
	Larray = []
	if re.match(r'^\s*x\s*$',logitemstr):
		return {}
	if re.match(r'^\s*\w{3}\s+\w{3}\s+\d\d?\s+(?:\d\d\:){2}\d\d\s+2[01]\d\d\s*$',logitemstr):
		return {'changetime':logitemstr.rstrip().lstrip()};

	if logitemstr.find("|") != -1:
		Lparts = logitemstr.lstrip().split('|')
		Larray.extend(Lparts)
	else:
		Larray.append(logitemstr)

	decompobj={}
	for dataitem in Larray:
		if logitemstr.find(":") != -1:
			datapieces = dataitem.lstrip().split(':',1)
			datakey = datapieces[0]
			decompobj[datakey] = datapieces[1]
	return decompobj

def decomposeFileLog(logstr, logtype=1):
	if (logtype == 1):
		Lparts = logstr.split(',',3)
		Lpathparts = Lparts[3].rsplit('/',1)
		Lnameparts = Lpathparts[1].rsplit('.',1)

		Lcompare = {}
		Lcompare['sha'] = Lparts[0].strip()
		Lcompare['bytesize'] = Lparts[1].strip()
		Lcompare['itemdatastr'] = Lparts[2].strip()
		Lcompare['itemdata'] = decomposeFileLogItemData(Lcompare['itemdatastr'])

		if 'mtype' in Lcompare['itemdata'].keys():
			Lcompare['mtype'] = Lcompare['itemdata']['mtype']
		else:
			Lcompare['mtype'] = 'md5'

		Lcompare['fullpath'] = Lparts[3].strip()
		Lcompare['path'] = Lpathparts[0]
		Lcompare['filename'] = Lpathparts[1]
		if len(Lnameparts)>1:
			Lcompare['filetype'] = Lnameparts[1]
		else:
			Lcompare['filetype'] = ''
		Lcompare['fulltext'] = logstr
		return Lcompare

def subprocHash(q,log,file,opts,filters=None):
	while True:
		if q is not None:
			fname=q.get()
		elif os.path.isfile(file):
			fname=file

		if fname is None:
			break
		fname = fname.replace("//","/")
#			fname = fname.replace(" ","\ ")
		print ('subprocess: ',fname)
		try:
			mtype='md5'
			if 'mtype' in opts.keys():
				mtype=opts['mtype']

			if mtype == 'md5':
				proc = subprocess.Popen(["/usr/bin/sigtool", "--md5", fname],stdout=subprocess.PIPE)
			elif mtype == 'sha1':
				proc = subprocess.Popen(["/usr/bin/sigtool", "--sha1", fname],stdout=subprocess.PIPE)
			elif mtype == 'sha256':
				proc = subprocess.Popen(["/usr/bin/sigtool", "--sha256", fname],stdout=subprocess.PIPE)
			else:
				return

			(out, err) = proc.communicate()
			logfile = open(log, "a+", -1)
			logfile.write(', '.join(out.split(':')[0:2])+', mtype:'+mtype+', x, '+fname+"\n")
			logfile.close()
			proc.wait()
		except OSError as exception:
			print (' ** OSERROR: ', fname)
			print (' ** - - ', exception.errno)
#			if exception.errno != errno.EEXIST:

		if q is not None:
			q.task_done()


def walkMD5Fast( dirpath, targetlog, opts ):
#	https://stackoverflow.com/questions/33152171/why-does-multiprocessing-process-join-hang
	num_threads=2
	if 'numthreads' in opts.keys():
		num_threads=opts['numthreads']

	namefilters=None
	if 'filters' in opts.keys():
		namefilters=opts['filters']

	filequeue=queue()
	threads=[]

	if 'walkmode' not in opts.keys():
		return

	walkMD5mode = opts['walkmode']
#	if 'threadprocess' in opts.keys():
	if walkMD5mode == 'threadprocess':
		for i in range(num_threads):
			worker = Thread(target=subprocHash, args=(filequeue,targetlog,dirpath,opts,namefilters))
			worker.setDaemon(True)
			threads.append(worker)
			worker.start()

		for folder,subs,files in os.walk(dirpath):
			for filename in files:

				fullpath=os.path.join(folder,filename)
				folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
				if (namefilters is None) or (not ignoreFile(filename,folderpath,fullpath,namefilters)):
					filequeue.put(fullpath)
		filequeue.join()

		for i in range(num_threads):
		    filequeue.put(None)
		for t in threads:
			t.join()
	if walkMD5mode == 'quickprocess':
		for folder,subs,files in os.walk(dirpath):
			for filename in files:

				fullpath=os.path.join(folder,filename)
				folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
				if (namefilters is None) or (not ignoreFile(filename,folderpath,fullpath,namefilters)):
					basepath = re.findall(r'^(.*\/)[^\/]+$',fullpath)[0]
					namestr = re.findall(r'^.*\/([^\/]+\S)\s*$',fullpath)[0]


					driveutils.logThisFile( basepath, namestr, logname, walkopts )
	if walkMD5mode == 'sigprocess':
		for folder,subs,files in os.walk(dirpath):
			for filename in files:

				fullpath=os.path.join(folder,filename)
				folderpath=re.findall('^(.*\/)[^\/]+\s*$',fullpath)[0]
				if (namefilters is None) or (not driveutils.ignoreFile(filename,folderpath,fullpath,namefilters)):
					basepath = re.findall(r'^(.*\/)[^\/]+$',fullpath)[0]
					namestr = re.findall(r'^.*\/([^\/]+\S)\s*$',fullpath)[0]


					subprocHash(None,logname,fname,walkopts,filters)


def shaSum(filename,count=64,style="md5"):
	if count is None:
		count=64
	if style == "md5":
		sha = hashlib.md5()
	if style == "sha1":
		sha = hashlib.sha1()
	if style == "sha256":
		sha = hashlib.sha256()
	with open(filename, 'rb') as f:
		for chunk in iter(lambda: f.read(count * 128 * sha.block_size), b''):
			sha.update(chunk)
	return sha.hexdigest()

def getFileInfo( path, count=None, opts=None ):
	if opts is None:
		opts={}

	sizeSt = -1
	try:
		sizeSt = os.path.getsize(path);
	except OSError as exception:
		sizeSt = -1

	try:
		mtype='md5'
		if 'mtype' in opts.keys():
			mtype=opts['mtype']

		if count is None:
			shaSt = shaSum(path,None,mtype)
		else:
			shaSt = shaSum(path,count,mtype)
	except OSError as exception:
		shaSt = "*********"
	except IOError as exception:
		shaSt = "**********"

	try:
		mTime = time.ctime(os.path.getmtime(path))
	except OSError as exception:
		mTime = "**********"

	Lcompare = {}

	textout = shaSt +', '+ str(sizeSt) +', mtype:'+mtype

#	textout +='|changetime:'+mTime

	textout +=', '+ path
	Lcompare['fulltext'] = textout

	Lcompare['sha'] = shaSt
	Lcompare['bytesize'] = str(sizeSt)
	Lcompare['itemdatastr'] = 'mtype:'+mtype
#	Lcompare['itemdatastr'] += '|changetime:'+mTime

	Lcompare['itemdata'] = decomposeFileLogItemData(Lcompare['itemdatastr'])
#	Lcompare['date'] = mTime
	Lcompare['fullpath'] = path

	Lpathparts = path.rsplit('/',1)
	Lnameparts = Lpathparts[1].rsplit('.',1)

	Lcompare['path'] = Lpathparts[0]
	Lcompare['filename'] = Lpathparts[1]

	if len(Lnameparts)>1:
		Lcompare['filetype'] = Lnameparts[1]
	else:
		Lcompare['filetype'] = ''
	return Lcompare



def logThisFile( fullpath, name, logfile, opts ):
	fname = fullpath + name

	count = None
	if 'useblocks' in opts.keys() and '_count' in opts['useblocks'].keys():
		count = int(opts['useblocks']['_count'])

	obj = getFileInfo( fname, count, opts )


	textout = obj['fulltext']

	fo = open( logfile, 'ab' )
	fo.write( textout+'\n' )
	fo.close()

	return obj



def addToLog( fulltext, log ):
	fo = open( log, 'ab' )
	fo.write( fulltext )
	fo.close()


def logCriticalError(text, otherlog):
	ret=re.findall("^(.*\/)",otherlog)
	lpath=ret[0]

	log = 'critical_errs.txt'
	fulltext = time.strftime(' %x %X ') +' - '+text

	fo = open( lpath+log, 'ab' )
	fo.write( fulltext )
	fo.close()

def readDir(path, logpath=None):
	try:
		listing = os.listdir(path)
	except OSError as exception:
		print ('******** err on '+str(exception))
		if logpath is not None:
			logCriticalError('failed to read path: ' +path, logpath)
			logCriticalError(str(exception), logpath)
			raise exception
			return None
		listing=[]

	for infile in listing:
		if infile == "." or infile == "..":
			listing.remove(infile)
	return listing

def executeProcess(proc):
	print ('start process')
	p = subprocess.Popen(proc, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#	for line in p.stdout.readlines():
#	    print line,
#	retval = p.wait()
	(output, err) = p.communicate()
	p_status = p.wait()
	print ('Status: ',p_status)
	return output


def executeMountProcess():
#	p = subprocess.Popen('mount', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#	(output, err) = p.communicate()
#	p_status = p.wait()
#	print 'Status: ',p_status
	output = check_output( [ 'mount' ] )
	print (output)
	return output

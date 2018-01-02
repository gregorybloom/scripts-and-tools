
import os, sys, hashlib, time, re
import copy
import subprocess
from subprocess import *

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
			print text
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

def createNewLog(logname, reuse=False):
#	print '- '+logname

	div = logname.find('/')
	if div >= 0:
		parts = logname.rsplit('/',1)
		path = parts[0]
		logname = parts[1]
#		print parts
	else:
		path=""

	if(  not os.path.exists(path)  ):
		try:
			print '****** '+path
			os.makedirs(path)
		except OSError as exception:
#			if exception.errno != errno.EEXIST:
			raise
	if reuse:
		fo = open( path +"/"+ logname, 'ab' )
		fo.close()
	else:
		fo = open( path +"/"+ logname, 'wb' )
		fo.close()

def decomposeFileLog(logstr, logtype):
	if (logtype == 1):
		Lparts = logstr.split(',',3)
		Lpathparts = Lparts[3].rsplit('/',1)
		Lnameparts = Lpathparts[1].rsplit('.',1)

		Lcompare = {}
		Lcompare['sha'] = Lparts[0].strip()
		Lcompare['bytesize'] = Lparts[1].strip()
		Lcompare['date'] = Lparts[2].strip()
		Lcompare['fullpath'] = Lparts[3].strip()
		Lcompare['path'] = Lpathparts[0]
		Lcompare['filename'] = Lpathparts[1]
		if len(Lnameparts)>1:
			Lcompare['filetype'] = Lnameparts[1]
		else:
			Lcompare['filetype'] = ''
		Lcompare['fulltext'] = logstr
		return Lcompare


def getFileInfo( path ):
	def shaSum(filename):
#	    sha = hashlib.sha256()
	    sha = hashlib.md5()
	    with open(filename, 'rb') as f:
	        for chunk in iter(lambda: f.read(128 * sha.block_size), b''):
	            sha.update(chunk)
	    return sha.hexdigest()

	sizeSt = -1
	try:
		sizeSt = os.path.getsize(path);
	except OSError as exception:
		sizeSt = -1

	try:
		shaSt = shaSum(path)
	except OSError as exception:
		shaSt = "*********"
	except IOError as exception:
		shaSt = "**********"

	try:
		mTime = time.ctime(os.path.getmtime(path))
	except OSError as exception:
		mTime = "**********"

	Lcompare = {}

	textout = shaSt +', '+ str(sizeSt) +', '+ mTime +', '+ path
	Lcompare['fulltext'] = textout

	Lcompare['sha'] = shaSt
	Lcompare['bytesize'] = str(sizeSt)
	Lcompare['date'] = mTime
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



def logThisFile( fullpath, name, logfile ):
	fname = fullpath + name

	obj = getFileInfo( fname )


	textout = obj['fulltext']

	fo = open( logfile, 'ab' )
	fo.write( textout+'\n' )
	fo.close()

	return textout



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
		print '******** err on '+str(exception)
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
	print 'start process'
	p = subprocess.Popen(proc, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#	for line in p.stdout.readlines():
#	    print line,
#	retval = p.wait()
	(output, err) = p.communicate()
	p_status = p.wait()
	print 'Status: ',p_status
	return output


def executeMountProcess():
#	p = subprocess.Popen('mount', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#	(output, err) = p.communicate()
#	p_status = p.wait()
#	print 'Status: ',p_status
	output = check_output( [ 'mount' ] )
	print output
	return output


import os, sys, hashlib, time, re
from maintenance_loader import *



logfolder = "logs"

logGroups = {}
logFiles = {}
i = 0


def beginFileListSplit(log, subfolder):
	setLogGroups()
	clearNewLogGroups(subfolder)
#	createNewLogGroups(subfolder)

	walkSplitFileList(log, subfolder)
#	countSplits(subfolder)


def setLogGroups():
	logFiles[''] = 'blanklog.txt'
	logFiles['jpg'] = 'jpglog.txt'
	logFiles['gif'] = 'giflog.txt'
	logFiles['png'] = 'pnglog.txt'
	logFiles['bmp'] = 'bmplog.txt'
	logFiles['html'] = 'htmllog.txt'
	logFiles['tif'] = 'tiflog.txt'
	logFiles['music'] = 'musiclog.txt'
	logFiles['txt'] = 'txtlog.txt'
	logFiles['mp3'] = 'mp3log.txt'
	logFiles['*stuff'] = 'stufflog.txt'
	logFiles['*misc'] = 'misclog.txt'

	logGroups[''] = {}
	logGroups[''][0] = ''
	logGroups['jpg'] = {}
	logGroups['jpg'][0] = 'jpg'
	logGroups['jpg'][1] = 'jpeg'
	logGroups['gif'] = {}
	logGroups['gif'][0] = 'gif'
	logGroups['png'] = {}
	logGroups['png'][0] = 'PNG'
	logGroups['png'][1] = 'png'
	logGroups['bmp'] = {}
	logGroups['bmp'][0] = 'bmp'
	logGroups['html'] = {}
	logGroups['html'][0] = 'html'

	logGroups['tif'] = {}
	logGroups['tif'][0] = 'tif'

	logGroups['music'] = {}
	logGroups['music'][0] = 'wav'
	logGroups['txt'] = {}
	logGroups['txt'][0] = 'txt'
	logGroups['mp3'] = {}
	logGroups['mp3'][0] = 'mp3'
	logGroups['mp3'][1] = 'MP3'
	logGroups['*stuff'] = {}
	logGroups['*stuff'][0] = 'db'
	logGroups['*stuff'][1] = 'chatlog'
	logGroups['*stuff'][2] = 'nib'
	logGroups['*stuff'][3] = 'htm'
	logGroups['*stuff'][4] = 'map'
	logGroups['*stuff'][5] = 'js'
	logGroups['*stuff'][6] = 'pdf'
	logGroups['*stuff'][7] = 'py'
	logGroups['*stuff'][8] = 'cfg'
	logGroups['*stuff'][9] = 'pyc'
	logGroups['*stuff'][10] = 'hpp'


def clearNewLogGroups(subfolder):
	path = logfolder+'/'+subfolder
	if(  not os.path.exists(path )  ):
		try:
			os.makedirs(path)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

	files = driveutils.readDir(path)
	for file in files:
		namestr = str(file)

		reg = r'.*.\txt$'
		if not os.path.isdir(path +'/'+ namestr):
			if re.search(reg,namestr):

				os.remove(path +'/'+ namestr)

def createNewLogGroups(subfolder):
	path = logfolder+'/'+subfolder
	if(  not os.path.exists(path )  ):
		try:
			os.makedirs(path)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

#	for (ltype, fname) in logFiles.items():
#		fo = open( path +"/"+ fname, 'wb' )
#		fo.close()



def walkSplitFileList(logA, subfolder):
	global i

	logAf = open(logfolder+'/'+logA, 'rb')

	i=0
	while 1:
		line = logAf.readline()
		if not line:
			break
#		if i>5000:
#			break

		i=i+1
		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if re.search(reg,line):
		
			Acompare = driveutils.decomposeFileLog(line,1)
			writeToSplitLog(Acompare, subfolder)


def findFileType(objA):

	for (ltype, list) in logGroups.items():

		for ftype in list.values():

			if objA['filetype'].strip() == ftype:
				return ltype;
	deftype = '*misc'
	return deftype


def writeToSplitLog(objA, subfolder):
	path = logfolder+'/'+subfolder+'/'

	ftype = objA['filetype'].strip()
	if( len(ftype)<2 ):
		ftype = ''

#	log = findFileType(objA)
#	fullpath = path+logFiles[log]

	log = objA['sha'][:2]+"-log.txt"
	fullpath = path+log

	if (i%100)==0:
		print ftype +' '+ log +' - ' + objA['fullpath']


	fulltext = objA['fulltext'].strip()

	fo = open( fullpath, 'ab' )
	fo.write( fulltext+'\n' )
	fo.close()


def countSplits(subfolder):
	print '\n'
	path = logfolder+'/'+subfolder+'/'

	fo = open( path +"/count.txt", 'wb' )
	fo.close()

	for (ltype, log) in logFiles.items():

		logAf = open(path+log, 'rb')

		i=0
		while 1:
			line = logAf.readline()
			if not line:
				break

			reg = r'^[A-Za-z0-9]+, [0-9]+,'
			if re.search(reg,line):
				i=i+1


		fulltext =  str(i)+ " '" +ltype+ "' files in " +path+log
		fo = open( path +"/count.txt", 'ab' )
		fo.write( fulltext+'\n' )

		print fulltext

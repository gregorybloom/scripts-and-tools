from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv
from sys import version_info



def sortLogBySHA(logpath):
	writefile = open(logpath+'.tmp', 'w')
	readfile = csv.reader(open(logpath), delimiter=",")
	filteredRows = filter(lambda x: len(x) > 3, readfile)
	for line in sorted(filteredRows, key=lambda line: line[0]):
		strng=','.join(line)
		writefile.write(strng+'\n')
	writefile.close()

	os.remove(logpath)
	os.rename(logpath+".tmp",logpath)

def logErredFiles(datasets,summarylog,useopts):
	driveutils.addToDebugLog( useopts, 'S1 - useopts keys : '+str(useopts.keys()) )
	if '_holddata' in useopts.keys():
		driveutils.addToDebugLog( useopts, 'S2 - useopts _holddata keys : '+str(useopts['_holddata'].keys()) )
		if 'droperr' in useopts['_holddata'].keys():
			driveutils.addToDebugLog( useopts, 'S3 - droperr length : '+str(len(useopts['_holddata']['droperr'])) )
			print '----------- errs: file loads failed -----------'
			driveutils.addToLog( "----------- errs: file loads failed -----------\n", summarylog )
			for obj in useopts['_holddata']['droperr']:
				driveutils.addToDebugLog( useopts, 'S4 : '+str(obj) )
				reline = obj['line']
#				reline = re.findall("^(?:[^,]+,){3}.*?(\/.*\/\/.*)$",reline)[0]

				print obj['runname'], ',', obj['logsetname'], ',', reline
				driveutils.addToLog( obj['runname']+','+obj['logsetname']+','+reline+"\n", summarylog )
			print '----------------------------------------------'
			driveutils.addToLog( "----------------------------------------------\n", summarylog )

	driveutils.addToDebugLog( useopts, 'S5 - datasets keys : '+str(datasets.keys()) )

	errfolderc=0
	if 'errset' in datasets.keys():
		driveutils.addToDebugLog( useopts, 'S6 - datasets errset keys : '+str(datasets['errset'].keys()) )
		if 'folderload' in datasets['errset'].keys():
			print '--------- errs: folder loads failed ---------'
			driveutils.addToLog( "--------- errs: folder loads failed ---------\n\n", summarylog )
			driveutils.addToDebugLog( useopts, 'S7 - datasets errset folderload keys : '+str(datasets['errset']['folderload'].keys()) )
			for logsetname,setobj in datasets['errset']['folderload'].iteritems():
				driveutils.addToDebugLog( useopts, 'S8 - '+logsetname+' : '+str(datasets['errset']['folderload'][logsetname].keys()) )
				for sourcename,folderlist in datasets['errset']['folderload'][logsetname].iteritems():
					driveutils.addToDebugLog( useopts, 'S9 - '+logsetname+' : '+sourcename+' len '+str(len(folderlist)) )
					for folderpath in folderlist:
						print logsetname,',', sourcename,' -  ',folderpath
						driveutils.addToLog( logsetname+', '+sourcename+' -  '+folderpath+"\n", summarylog )
						errfolderc+=1
			print '----------------------------------------------'
			driveutils.addToLog( "----------------------------------------------\n", summarylog )
	driveutils.addToDebugLog( useopts, 'S10 - done ' )



def logFolderDupes(datasets,summarylog,useopts,run,logfolder,timestamp):
#	def saveLastDupes():


	driveutils.addToDebugLog( useopts, 'T1 - useopts _holddata keys : '+str(useopts['_holddata'].keys()) )
	if 'folderdupes' in useopts['_holddata'].keys():
		useopts['_holddata']['matchingsets']={}

		logpath = logfolder+'/md5dupes/'+run+'/';
		sublogfolder = logpath+'master/master-'+timestamp+'/'

		driveutils.addToDebugLog( useopts, 'T2 - '+run+' keys : '+str(useopts['_holddata']['folderdupes'][run].keys()) )
		for logsetname,obj2 in useopts['_holddata']['folderdupes'][run].iteritems():
			listdupelog = sublogfolder + 'lists/md5dupes-dupes-'+logsetname+'-'+datasets['timestr']+'.txt'
			driveutils.addToDebugLog( useopts, 'T3 - '+run+','+logsetname+' : '+str(os.path.isfile(listdupelog)) )
			if os.path.exists(listdupelog) and os.path.isfile(listdupelog):
				sortLogBySHA(listdupelog)
				dupelistobj = loadMasterLogObj(listdupelog)
				driveutils.addToDebugLog( useopts, 'T4 - dupelistobj '+run+','+logsetname+' : '+str(dupelistobj) )

				lastsha=""
				lastpath=""
				curfolders=[]
				while True:
					driveutils.addToDebugLog( useopts, 'T5 - '+run+','+logsetname+'. dupelistobj : '+str(dupelistobj) )
					loadMasterObj(dupelistobj)
					loadMasterObjVals(dupelistobj)
					driveutils.addToDebugLog( useopts, 'T6 - '+run+','+logsetname+'. dupelistobj : '+str(dupelistobj) )

					driveutils.addToDebugLog( useopts, 'T7 - '+run+','+logsetname+' : '+str(dupelistobj.keys()) )
					if(dupelistobj['line'] is None):
						driveutils.addToDebugLog( useopts, 'T7.1 - '+run+','+logsetname+' : '+str(dupelistobj.keys()) )
						break
					driveutils.addToDebugLog( useopts, 'T8 - '+run+','+logsetname+' : '+str(dupelistobj.keys()) )
					if(dupelistobj['cur_sha'] is None and dupelistobj['cur_path'] is None):
						driveutils.addToDebugLog( useopts, 'T8.1 - '+run+','+logsetname+' : '+str(dupelistobj.keys()) )
						break

					driveutils.addToDebugLog( useopts, 'T9 - '+run+','+logsetname+' : '+lastsha+' == '+dupelistobj['cur_sha']+','+str(lastsha==dupelistobj['cur_sha']) )
					if lastsha=="" or lastsha==dupelistobj['cur_sha']:
#						if(lastsha==dupelistobj['cur_sha']):
						driveutils.addToDebugLog( useopts, 'T10.1 - '+run+','+logsetname+' : '+str(len(curfolders))+', '+lastsha+', '+lastpath )
						curfolders.append(dupelistobj['folder_path'])
						lastsha=dupelistobj['cur_sha']
						lastpath=dupelistobj['cur_path']
						driveutils.addToDebugLog( useopts, 'T10.2 - '+run+','+logsetname+' : '+str(len(curfolders))+', '+lastsha+', '+lastpath )
					else:
						driveutils.addToDebugLog( useopts, 'T10.3 - '+str(run)+','+str(logsetname)+' : '+str(len(curfolders)) )
						if len(curfolders)>1:
							foldersha=""
							driveutils.addToDebugLog( useopts, 'T10.4 - '+str(run)+','+str(logsetname)+' : '+str(foldersha)+','+str(len(curfolders)) )
							for folder in curfolders:
								hash_object = hashlib.sha256(str.encode(folder))
								hex_dig = hash_object.hexdigest()
								foldersha=foldersha+hex_dig
								driveutils.addToDebugLog( useopts, 'T11.1 - '+run+','+logsetname+' : '+folder+', '+foldersha )
							driveutils.addToDebugLog( useopts, 'T11.2 - '+run+','+logsetname+' : '+str(len(curfolders)) )
							for folder in curfolders:
								AddToTotal('matchingsets',useopts,[run,logsetname,foldersha,folder])
								driveutils.addToDebugLog( useopts, 'T11.3 - '+run+','+logsetname+' : '+foldersha+', '+folder )
								AddToTotal('matchingshasets',useopts,[run,logsetname,foldersha,folder,lastsha])

						driveutils.addToDebugLog( useopts, 'T12 - '+run+','+logsetname+' : '+str(len(curfolders)) )
#						if len(curfolders)==1:
#							wtftxt = "*1** "+lastsha+", "+str(curfolders)+", "+lastpath
#							driveutils.addToDebugLog( useopts, 'T13 - '+run+','+logsetname+' : '+wtftxt )

#						driveutils.addToLog( "\n", listdupelog+".sha.ingroups.txt" )

						curfolders=[]
						lastsha=dupelistobj['cur_sha']
						lastpath=dupelistobj['cur_path']
						curfolders.append(dupelistobj['folder_path'])
						driveutils.addToDebugLog( useopts, 'T14 - '+run+','+logsetname+' : '+lastsha+','+lastpath+','+str(len(curfolders))+','+dupelistobj['folder_path'] )

					driveutils.addToDebugLog( useopts, 'T15 - '+run+','+logsetname+' : '+str(dupelistobj) )
					incrementMasterObj(dupelistobj)
					driveutils.addToDebugLog( useopts, 'T16 - '+run+','+logsetname+' : '+str(dupelistobj) )

				driveutils.addToDebugLog( useopts, 'T17 - '+run+','+logsetname+' : '+str(len(curfolders)) )
				if len(curfolders)>1:
					foldersha=""
					driveutils.addToDebugLog( useopts, 'T18 - '+run+','+logsetname+' : '+str(len(curfolders)) )
					for folder in curfolders:
						hash_object = hashlib.sha256(str.encode(folder))
						hex_dig = hash_object.hexdigest()
						foldersha=foldersha+hex_dig
						driveutils.addToDebugLog( useopts, 'T19 - '+run+','+logsetname+' : '+folder+', '+foldersha )
					for folder in curfolders:
						AddToTotal('matchingsets',useopts,[run,logsetname,foldersha,folder])
						driveutils.addToDebugLog( useopts, 'T20 - '+run+','+logsetname+' : '+foldersha+', '+folder )
						AddToTotal('matchingshasets',useopts,[run,logsetname,foldersha,folder,lastsha])

					driveutils.addToDebugLog( useopts, 'T21 - '+run+','+logsetname+' : '+str(len(curfolders)) )
					if len(curfolders)==1:
						wtftxt = "*2** "+lastsha+", "+str(curfolders)+", "+lastpath
						driveutils.addToDebugLog( useopts, 'T22 - '+run+','+logsetname+' : '+wtftxt )

				closeUpFiles(dupelistobj)

		print '----------- folder groups sharing dupes -----------'
		driveutils.addToLog( "----------- folder groups sharing dupes -----------\n", summarylog )
		driveutils.addToDebugLog( useopts, 'T23 - '+run+' : '+str(useopts['_holddata']['matchingsets'].keys()) )
		for runname,obj in useopts['_holddata']['matchingsets'].iteritems():
			driveutils.addToDebugLog( useopts, 'T24 - '+run+','+runname+' : '+str(useopts['_holddata']['matchingsets'][runname].keys()) )
			for logsetname,obj2 in useopts['_holddata']['matchingsets'][runname].iteritems():
				driveutils.addToDebugLog( useopts, 'T25 - '+run+','+runname+','+logsetname+' : '+str(useopts['_holddata']['matchingsets'][runname][logsetname].keys()) )
				for foldersha,obj3 in useopts['_holddata']['matchingsets'][runname][logsetname].iteritems():
					driveutils.addToDebugLog( useopts, 'T26 - '+run+','+runname+','+logsetname+','+foldersha+' : '+str(useopts['_holddata']['matchingsets'][runname][logsetname][foldersha].keys()) )
					print '--------------------------------'
					driveutils.addToLog( "--------------------------------\n", summarylog )
					for folderpath,countS in useopts['_holddata']['matchingsets'][runname][logsetname][foldersha].iteritems():
						driveutils.addToDebugLog( useopts, 'T27 - '+run+','+runname+','+logsetname+','+foldersha+','+folderpath+' ' )
						countT = useopts['_holddata']['folder'][runname][folderpath]+1
						shaset = useopts['_holddata']['folderdupesha'][runname][logsetname][folderpath]
						countD = len(sorted(set(shaset.keys())))
#						matchcount=len(foldersha)/64
						countS+=1
						textstr = runname+", "+logsetname+":   "+ str(countS)+"/"+str(countT)+", "+ str(100*countS/countT)+"%"+" dupes in set;  "+str(countD)+"/"+str(countT)+", "+ str(100*countD/countT)+"%"+" dupes overall,  "+ folderpath
						print textstr
						driveutils.addToLog( textstr+"\n", summarylog )
						driveutils.addToDebugLog( useopts, 'T28.1 - '+foldersha+','+folderpath+' : '+textstr )

#						for folderpath,obj in useopts['_holddata']['matchingshasets'][runname][logsetname][foldersha].iteritems():
#							for sha,obj2 in useopts['_holddata']['matchingshasets'][runname][logsetname][foldersha][folderpath].iteritems():
##								driveutils.addToLog( '. '+sha+"\n", summarylog )
#								print '. ',sha

					driveutils.addToDebugLog( useopts, 'T29 - '+run+','+runname+','+logsetname )
				print '----------------------------------------------'
				driveutils.addToLog( "----------------------------------------------\n", summarylog )
				driveutils.addToDebugLog( useopts, 'T30 - '+run+','+runname+','+logsetname )

		driveutils.addToDebugLog( useopts, 'T31 - '+run )
		print
		print '----------- folders overall -----------'
		driveutils.addToLog( "\n----------- folders with dupes -----------\n", summarylog )
		driveutils.addToDebugLog( useopts, 'T32 - '+run+' : '+str(useopts['_holddata']['folderdupes'].keys()) )
		for runname,obj in useopts['_holddata']['folderdupes'].iteritems():
			driveutils.addToDebugLog( useopts, 'T33 - '+run+','+runname+' : '+str(useopts['_holddata']['folderdupes'][runname].keys()) )
			for logsetname,obj2 in useopts['_holddata']['folderdupesha'][runname].iteritems():
				driveutils.addToDebugLog( useopts, 'T33 - '+run+','+runname+','+logsetname+' : '+str(useopts['_holddata']['folderdupes'][runname][logsetname].keys()) )
				for folderpath,shaset in useopts['_holddata']['folderdupesha'][runname][logsetname].iteritems():
					countD = useopts['_holddata']['folderdupes'][runname][logsetname][folderpath]+1
					countT = useopts['_holddata']['folder'][runname][folderpath]+1
					textstr = runname+", "+logsetname+":   "+ str(countD)+"/"+str(countT)+", "+ str(100*countD/countT)+"%"+" dupes overall,  "+ folderpath
					print textstr
					driveutils.addToLog( textstr+"\n", summarylog )
					driveutils.addToDebugLog( useopts, 'T34 - '+folderpath+' : '+textstr )
				driveutils.addToDebugLog( useopts, 'T35 - '+run+','+runname+','+logsetname )
			driveutils.addToDebugLog( useopts, 'T36 - '+run+','+runname )

		print '----------------------------------------------'
		driveutils.addToLog( "----------------------------------------------\n", summarylog )
		driveutils.addToDebugLog( useopts, 'T37 - '+run )

def beginCompareStage(loglist,runname,logfolder,masterroute,timestamp,targetlist,datasets,useopts=None):
	if useopts is None:
		useopts={}
	useopts['_holddata']={}

	logpath = logfolder+'/md5dupes/'+runname+'/';

	summarylog = logpath+'master/md5dupes-summary-'+timestamp+'.txt'
	sublogfolder = logpath+'master/master-'+timestamp+'/'

	debuglog = sublogfolder + 'md5dupes-debug-'+datasets['timestr']+'.txt'
	driveutils.addToDebugLog( useopts,"----- "+runname+" -----\n",debuglog)


	logsdict={}
	logsdict['logs']={}
	logsdict['folders']={}
	logsdict['logs']['summary']=summarylog
	logsdict['folders']['logpath']=logpath
	logsdict['folders']['sublogs']=sublogfolder

	print
	for comparelog in loglist:
		driveutils.addToDebugLog( useopts, '***************************' )
		driveutils.addToDebugLog( useopts, '***************************' )
		driveutils.addToDebugLog( useopts, 'A '+runname+','+comparelog['setname']+' : isfile: ' +str(comparelog) )

		if 'log' in comparelog.keys():
#			print comparelog
			stepCompareLogs(runname,logsdict,comparelog['log'],comparelog['setname'],targetlist,datasets,useopts)


	logpath = logfolder+'/md5dupes/'+runname+'/';
	sublogfolder = logpath+'master/master-'+timestamp+'/'
	listlog = sublogfolder+'tmp/md5dupes-list-'+timestamp+'.txt'
	driveutils.createNewLog(listlog,False)
	driveutils.addToDebugLog( useopts, 'P '+listlog )
	for comparelog in loglist:
		driveutils.addToDebugLog( useopts, 'Q1 '+str(comparelog) )
		if 'log' in comparelog.keys():
			with open(comparelog['log']) as f:
			    with open(listlog, "a") as f1:
					driveutils.addToDebugLog( useopts, 'Q2 read- '+str(comparelog['log']) )
					driveutils.addToDebugLog( useopts, 'Q3 append- '+listlog )
					for line in f:
						driveutils.addToDebugLog( useopts, 'Q~ '+str(line) )
						f1.write(line)
	sortLogBySHA(listlog)
	driveutils.addToDebugLog( useopts, 'R1 sort '+listlog )


	driveutils.createNewLog(summarylog,True)
	driveutils.addToDebugLog( useopts, 'R2 sort '+summarylog )
	print '----------------------------------------------'
	print
	driveutils.addToLog( "----------------------------------------------\n\n", summarylog )
	logErredFiles(datasets,summarylog,useopts)
	logFolderDupes(datasets,summarylog,useopts,runname,logfolder,timestamp)
	driveutils.addToDebugLog( useopts, 'U1 sort '+summarylog )

	print
	print '----------------------------------------------'
	print '---------------totals---------------------'
	driveutils.addToLog( "\n----------------------------------------------\n", summarylog )
	driveutils.addToLog( "---------------totals---------------------\n", summarylog )

	driveutils.addToDebugLog( useopts, 'U2 : '+str(useopts['_holddata']['overalltotals'].keys()) )
	for runname,runset in useopts['_holddata']['overalltotals'].iteritems():
		driveutils.addToDebugLog( useopts, 'U3 '+runname+' : '+str(useopts['_holddata']['overalltotals'][runname].keys()) )
		for logsetname,logval in useopts['_holddata']['overalltotals'][runname].iteritems():
			driveutils.addToDebugLog( useopts, 'U4 '+runname+','+logsetname+' : '+str(useopts['_holddata']['overalltotals'][runname][logsetname]) )

			countD = 0
			driveutils.addToDebugLog( useopts, 'U5 '+runname+','+logsetname+' : '+runname+' == '+str(useopts['_holddata']['totals'].keys()) )
			if runname in useopts['_holddata']['totals'].keys():
				driveutils.addToDebugLog( useopts, 'U6 '+runname+','+logsetname+' : '+logsetname+' == '+str(useopts['_holddata']['totals'][runname].keys()) )
				if logsetname in useopts['_holddata']['totals'][runname].keys():
					countD = useopts['_holddata']['totals'][runname][logsetname]+1
					driveutils.addToDebugLog( useopts, 'U7 '+runname+','+logsetname+' : '+str(countD)+', '+str(useopts['_holddata']['totals'][runname][logsetname]) )
			countT = useopts['_holddata']['overalltotals'][runname][logsetname]+1
			driveutils.addToDebugLog( useopts, 'U8 '+runname+','+logsetname+' : '+str(countT)+', '+str(useopts['_holddata']['overalltotals'][runname][logsetname]) )
			textstr = runname+", "+logsetname+":   "+ str(countD)+"/"+str(countT)+", "+ str(100*countD/countT)+"%"+" duplicates in total"
			print textstr
			driveutils.addToLog( textstr+"\n", summarylog )
			driveutils.addToDebugLog( useopts, 'U9 '+runname+','+logsetname+' : '+textstr )


	logpath = logfolder+'/md5dupes/'+runname+'/';
	sublogfolder = logpath+'master/master-'+timestamp+'/'
	newlog = sublogfolder + 'md5dupes-'+logsetname+'-'+datasets['timestr']+'.txt'
	print
	print newlog
	driveutils.addToDebugLog( useopts, 'U10 '+newlog )

	useopts['_holddata']['overalltotals']={}



def loadMasterLogObj(masterpath,a=0):
	masterdict={}
	if a == 0:
		logAf = open(masterpath, 'rb')
	else:
		logAf = open(masterpath, 'ab')
	masterdict={}
	masterdict['obj']=logAf
	masterdict['pos']=0
	masterdict['logpath']=masterpath
	masterdict['logname']=re.findall("^.*\/([^\/]+\.\w+)\s*$",masterpath)[0]
	return masterdict
def closeUpFiles(masterobj):
	if 'obj' in masterobj.keys():
		masterobj['obj'].close()

def incrementMasterObj(masterobj):
	masterobj['pos']=masterobj['obj'].tell()
def resetMasterObjPos(masterobj):
	curpos=masterobj['obj'].tell()
	if curpos != masterobj['pos']:
		masterobj['obj'].seek( masterobj['pos'] )
def loadMasterObj(masterobj):
	logObj = masterobj['obj']

	if 'pos' in masterobj.keys():
		resetMasterObjPos(masterobj)
		aline=logObj.readline()
		masterobj['line']=aline
def loadMasterObjVals(masterobj):
	reg = r'^[A-Za-z0-9]+, [0-9]+,'
	regE1 = r'^\*+, \-?[0-9]+,'
	regE2 = r'^(?:\*|[0-9])+, \*+,'
	regE3 = r'^[A-Za-z0-9]+, -1,'

	if 'loadErr' in masterobj.keys():
		del masterobj['loadErr']

	if 'line' in masterobj.keys():
		if re.search(reg,masterobj['line']):
			l = masterobj['line']
			Acompare = driveutils.decomposeFileLog(masterobj['line'],1)
			masterobj['cur_sha']=Acompare['sha']

			groups = re.findall(r'^(.*\/)[^\/]*$',Acompare['fullpath'])
			masterobj['folder_path']=groups[0]

			groups = re.findall(r'\/(\/.*)$',Acompare['fullpath'])
			masterobj['cur_path']=groups[0]

			masterobj['line']=l
		elif re.search(regE1,masterobj['line']) or re.search(regE2,masterobj['line']) or re.search(regE3,masterobj['line']):
			l = masterobj['line']
			Acompare = driveutils.decomposeFileLog(masterobj['line'],1)
			masterobj['cur_sha']=Acompare['sha']

			groups = re.findall(r'\/(\/.*)$',Acompare['fullpath'])
			masterobj['cur_path']=groups[0]
			masterobj['loadErr']=True
			masterobj['line']=l
		else:
			masterobj['cur_path']=None
			masterobj['cur_sha']=None

def stepCompareLogs(runname,logsdict,targetlog,logsetname,targetlist,datasets,useopts=None):
#	def ssdfsdf(masterobj,compareinfo):
	listlog = logsdict['folders']['sublogs'] + 'lists/md5dupes-list-'+logsetname+'-'+datasets['timestr']+'.txt'
	listdupelog = logsdict['folders']['sublogs'] + 'lists/md5dupes-dupes-'+logsetname+'-'+datasets['timestr']+'.txt'

	newlog = logsdict['folders']['sublogs'] + 'md5dupes-'+logsetname+'-'+datasets['timestr']+'.txt'

	driveutils.createNewLog(listlog,False)
	listlogobj = loadMasterLogObj(listlog,2)
	driveutils.createNewLog(listdupelog,False)
	listdupelogobj = loadMasterLogObj(listdupelog,2)

	driveutils.createNewLog(newlog,False)
	newlogobj = loadMasterLogObj(newlog,2)
	masterobj = loadMasterLogObj(targetlog)
	compareinfo={}

	dset=-1
	c=0
	opath=''
	trackDupes=False
	setnamestr=runname+','+logsetname
	driveutils.addToDebugLog( useopts, 'B '+setnamestr )
	while True:
		driveutils.addToDebugLog( useopts, 'C '+setnamestr+' : masterBef: ' +str(masterobj) )
		loadMasterObj(masterobj)
		loadMasterObjVals(masterobj)
		driveutils.addToDebugLog( useopts, 'D '+setnamestr+' : masterAft: ' +str(masterobj) )

		driveutils.addToDebugLog( useopts, 'E '+setnamestr+' : master keys: ' +str(masterobj.keys()) )
		if 'loadErr' in masterobj.keys() and masterobj['loadErr'] == True:
			if 'droperr' not in useopts['_holddata'].keys():
				useopts['_holddata']['droperr']=[]
			driveutils.addToDebugLog( useopts, 'F1 '+setnamestr+' : errs#: ' +str(len(useopts['_holddata']['droperr'])) )
			useopts['_holddata']['droperr'].append({'line':masterobj['line'],'runname':runname,'logsetname':logsetname})
			driveutils.addToDebugLog( useopts, 'F2 '+setnamestr+' : new err: ' +str(useopts['_holddata']['droperr'][-1]) )

		else:
			driveutils.addToDebugLog( useopts, 'F3 '+setnamestr+' : add up' )
			listlogobj['obj'].write(masterobj['line'])
			AddToTotal('overall',useopts,[runname,logsetname])
			AddToTotal('folder',useopts,[runname,masterobj['folder_path']])
			driveutils.addToDebugLog( useopts, 'F4 '+setnamestr+' : folder path ' +masterobj['folder_path'] )

			driveutils.addToDebugLog( useopts, 'G1 '+setnamestr+' : masterobj keys ' +str(masterobj.keys()) )
			if 'cur_sha' in masterobj.keys() and masterobj['cur_sha'] is not None:
				driveutils.addToDebugLog( useopts, 'G2 '+setnamestr+' : masterobj keys ' +str(masterobj.keys()) )
				if 'last_sha' in compareinfo.keys() and compareinfo['last_sha'] is not None:
					driveutils.addToDebugLog( useopts, 'G3 '+setnamestr+' : '+str(trackDupes)+' SHAs ' +masterobj['cur_sha']+' == '+compareinfo['last_sha']+' => '+str(masterobj['cur_sha'] == compareinfo['last_sha']) )
					if masterobj['cur_sha'] == compareinfo['last_sha']:
						driveutils.addToDebugLog( useopts, 'G4 '+setnamestr+' : compareinfo keys ' +str(compareinfo.keys()) )
						if 'line' in compareinfo.keys():
							driveutils.addToDebugLog( useopts, 'G5 '+setnamestr+' : dset ' +str(dset)+','+str(c) )
							if dset<0:
								dset=c
							driveutils.addToDebugLog( useopts, 'G6 '+setnamestr+' : compareinfo line ' +compareinfo['line'].rstrip() )
							print compareinfo['line'].rstrip()
							newlogobj['obj'].write(compareinfo['line'])
							listdupelogobj['obj'].write(masterobj['line'].rstrip()+"\n")
							AddToTotal('totals',useopts,[runname,logsetname])
							AddToTotal('folderdupes',useopts,[runname,logsetname,masterobj['folder_path']])
							AddToTotal('folderdupesha',useopts,[runname,logsetname,masterobj['folder_path'],masterobj['cur_sha']])
							AddToTotal('foldermatchset',useopts,[runname,logsetname,dset,masterobj['folder_path']])
							driveutils.addToDebugLog( useopts, 'G7 '+setnamestr+' : folder dupes' )
							trackDupes = True
					elif trackDupes == True:
						driveutils.addToDebugLog( useopts, 'H1 '+setnamestr+' : dset ' +str(dset)+','+str(c) )
						if dset<0:
							dset=c
						trackDupes=False
						driveutils.addToDebugLog( useopts, 'H2 '+setnamestr+' : compareinfo line ' +compareinfo['line'].rstrip() )
						print compareinfo['line'].rstrip()
						newlogobj['obj'].write(compareinfo['line'])
						listdupelogobj['obj'].write(masterobj['line'].rstrip()+"\n")
						AddToTotal('totals',useopts,[runname,logsetname])
						AddToTotal('folderdupes',useopts,[runname,logsetname,masterobj['folder_path']])
						AddToTotal('folderdupesha',useopts,[runname,logsetname,masterobj['folder_path'],masterobj['cur_sha']])
						AddToTotal('foldermatchset',useopts,[runname,logsetname,dset,masterobj['folder_path']])
						driveutils.addToDebugLog( useopts, 'H3 '+setnamestr+' : dset ' +str(dset) )
						print '-----------------------------------------'
						newlogobj['obj'].write('-----------------------------------------\n')
						dset=-1
#		print masterobj['pos'],'== ',masterobj['cur_sha'],masterobj['line'].rstrip()


		driveutils.addToDebugLog( useopts, 'I1 '+setnamestr+' : masterobj ' +str(masterobj['line']) )

		if(masterobj['line'] is None):
			break
		driveutils.addToDebugLog( useopts, 'I2 '+setnamestr+' : masterobj ' +str(masterobj['cur_sha']) + ','+str(masterobj['cur_path']) )
		if(masterobj['cur_sha'] is None and masterobj['cur_path'] is None):
			break
		driveutils.addToDebugLog( useopts, 'I3 '+setnamestr+' : masterobj ' +str(masterobj) )

		compareinfo['line'] = masterobj['line']
		compareinfo['last_sha'] = masterobj['cur_sha']
		compareinfo['pos'] = masterobj['pos']

		driveutils.addToDebugLog( useopts, 'J '+setnamestr+' : masterobj ' +str(compareinfo) )
		driveutils.addToDebugLog( useopts, 'K1 '+setnamestr+' : masterobj ' +str(masterobj) )
		incrementMasterObj(masterobj)
		driveutils.addToDebugLog( useopts, 'K2 '+setnamestr+' : masterobj ' +str(masterobj) )
		c+=1

	driveutils.addToDebugLog( useopts, 'L '+setnamestr+' : trackDupes ' +str(trackDupes) )
	if trackDupes == True:
		driveutils.addToDebugLog( useopts, 'M1 '+setnamestr+' : dset ' +str(dset)+','+str(c) )
		if dset<0:
			dset=c
		trackDupes=False
		driveutils.addToDebugLog( useopts, 'M2 '+setnamestr+' : compareinfo line ' +compareinfo['line'].rstrip() )
		newlogobj['obj'].write(compareinfo['line'])
		listdupelogobj['obj'].write(masterobj['line'].rstrip()+"\n")
		AddToTotal('totals',useopts,[runname,logsetname])
		AddToTotal('folderdupes',useopts,[runname,logsetname,masterobj['folder_path']])
		AddToTotal('folderdupesha',useopts,[runname,logsetname,masterobj['folder_path'],masterobj['cur_sha']])
		AddToTotal('foldermatchset',useopts,[runname,logsetname,dset,masterobj['folder_path']])
		driveutils.addToDebugLog( useopts, 'M3 '+setnamestr+' : dset ' +str(dset) )
		print compareinfo['line'].rstrip()
		print '-----------------------------------------'
		newlogobj['obj'].write('-----------------------------------------\n')
#		useopts['_holddata']['totals'][runname][logsetname]

#	for n,v in masterobj.iteritems():
#		print '   .. ',n,'=',v
#	for n,v in logsdict.iteritems():
#		print '   -- ',n,'=',v

	print
#	actOnUseOpts('end',useopts,steplist,masterlist,runname,logsetname,{})

	closeUpFiles(masterobj)
	closeUpFiles(newlogobj)
	closeUpFiles(listlogobj)
	driveutils.addToDebugLog( useopts, 'N '+setnamestr+' ! ' )

#	os.rename(newmasterlog+".tmp",newmasterlog)
	sortLogBySHA(targetlog)

def AddToTotal(totype,useopts,valset,d=0):
	if d == 0:
		driveutils.addToDebugLog( useopts, '.. !.a  : Add To Total: '+str(valset) )
		if totype == 'overall':
			totype = 'overalltotals'
		arrg=['_holddata']
		arrg.append(totype)
		arrg.extend(valset)
		driveutils.createDictSet(useopts,arrg[0:-1])
	else:
		arrg=valset

	driveutils.addToDebugLog( useopts, '.. !.b  : valset: '+str(valset)+' to '+totype )
	oname=arrg.pop(0)
	driveutils.addToDebugLog( useopts, '.. !.c  : '+str(oname)+', valset: '+str(valset) )
	if len(arrg)>0:
		driveutils.addToDebugLog( useopts, '.. !.d'+str(d)+'  : added total: '+str(oname)+'='+str(useopts[oname].keys()) )
		AddToTotal(totype,useopts[oname],arrg,(d+1))
	else:
		if oname not in useopts.keys():
			useopts[oname]=0
		else:
			useopts[oname]+=1
		driveutils.addToDebugLog( useopts, '.. !.e  : added total: '+str(oname)+'='+str(useopts[oname]) )

	if d==0:
		driveutils.addToDebugLog( useopts, '.. !.f  : added total: ' +str(len(useopts['_holddata'].keys())) )



def WalkThroughLog(c,runname,logsdict,targetlog,logsetname,targetlist,datasets,useopts):
	return

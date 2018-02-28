from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv


def concatLogGroups(logparts):
	newloglist=[]
	for loggroup,grouplogs in logparts.iteritems():
		if 'partlog' in grouplogs.keys():
			if 'logs' in grouplogs.keys():
				newlogname = grouplogs['partlog']

				driveutils.createNewLog(newlogname,False)

				newlog = open(newlogname, 'ab')

				loglist = grouplogs['logs']
				for logitem in loglist:
					flogobj = open(logitem, 'r')
					for line in flogobj:
						newlog.write(line)
					flogobj.close()
				newlog.close()

				comparedata.sortLogByPath(newlogname)
				newloglist.append(newlogname)
	return newloglist



def grabAMasterLog(masterpath,timestamp,useopts):
	masterlog = getBestMaster(masterpath, useopts)

	if masterlog == None:
		vals = timestamp.split('-')
		val1 = int(vals[0])
		val2 = int(vals[1])-1
		while( len(str(val2)) < 6 ):
			# adds 0's to clock time denomination as necessary
			val2="0"+str(val2)

#			masterlog = 'md5vali-master-'+str(val1)+'-'+str(val2)+'.txt'
		masterlog = 'master-'+str(val1)+'-'+str(val2)+'/'
		masterlog += 'md5vali-master-'+str(val1)+'-'+str(val2)+'.txt'
		driveutils.createNewLog(masterpath+masterlog,False)
	masterlog=masterpath+masterlog
	return masterlog

def getBestMaster(masterpath,useopts):
	def checkMasterName(val1,val2,masterpath):
		val1i=val1
		val2i=val2
		mastername = buildMasterName(val1i,val2i)
		mpath = masterpath+mastername
		if os.path.exists(mpath):
			return True
		return False

	def buildMasterName(val1,val2):
		while( len(str(val1)) < 8 ):
			# adds 0's to clock time denomination as necessary
			val1="0"+str(val1)
		while( len(str(val2)) < 6 ):
			# adds 0's to clock time denomination as necessary
			val2="0"+str(val2)
		bestfit=str(val1)+'-'+str(val2)
		bestmaster = 'master-'+bestfit+'/'
		bestmaster += 'md5vali-master-'+bestfit+'.txt'
		return bestmaster

	if not os.path.exists(masterpath):
		try:
			os.makedirs(masterpath)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

	highmaster = None
	try:
		masterlist = driveutils.readDir(masterpath)
	except OSError as exception:
		raise
	if len(masterlist) == 0:
		return None
	masterlist.sort()

	bestfit1=0
	bestfit2=0
	for mastern in masterlist:
		namestr = str(mastern)
#		if re.match('^md5vali-master-\d+-\d+\.txt\s*$',namestr):
#			groups = re.findall(r'^md5vali-master-(\d+-\d+)\.txt\s*$',namestr)
		if re.match('^master-\d+-\d+\s*$',namestr):
			groups = re.findall(r'^master-(\d+-\d+)\s*$',namestr)
			vals = groups[0].split('-')
			val = int(vals[0])

			if(val > bestfit1):
				if(checkMasterName(val,int(vals[1]),masterpath)==True):
					bestfit1=val
					bestfit2=int(vals[1])
			elif(val == bestfit1):
				if(bestfit2 < int(vals[1])):
					if(checkMasterName(val,int(vals[1]),masterpath)==True):
						bestfit1=val
						bestfit2=int(vals[1])

	if(bestfit1 > 0) and (bestfit2 > 0):
		bestmaster = buildMasterName(bestfit1,bestfit2)
		return bestmaster


def createNewTmpMD5Logs(groupname,timestr,infosets,foundlist,logfolder,md5opts=None):
	if md5opts is None:
		md5opts={}
	if 'walkopts' not in md5opts.keys():
		md5opts['walkopts']={}

	logset={}
	mastset={}
	errset={}
	loglist=[]

	if groupname not in logset.keys():
		logset[groupname]={}
	logpath = logfolder+'/md5vali/'+groupname+'/';


	if 'usemd5log' in md5opts['walkopts'].keys():

		uselog=md5opts['walkopts']['usemd5log']['logpath']
		if os.path.exists(uselog) and os.path.isfile(uselog):
			print "Using ",uselog

			if 'foldersets' in infosets.keys():
				for setname,folderset in infosets['foldersets'].iteritems():
					for sourcename,folderpath in folderset.iteritems():

						if sourcename != md5opts['walkopts']['usemd5log']['setsource']:
							continue
						if sourcename not in foundlist.keys():
							continue

						if setname not in logset[groupname].keys():
							logset[groupname][setname]={}

						startpath=foundlist[sourcename]
						targetpath=startpath+folderpath
						targetpath = targetpath.replace('//','/')
						targetpath = targetpath.rstrip('/')
						targetpath = targetpath+'/'


						logname= logpath+'pieces/'+sourcename+'/'+setname+'/md5vali-'+sourcename+'-'+timestr+'.txt'
						driveutils.createNewLog(logname,True)
						filelog = open(logname, "a")

						with open(uselog) as f:
						    for rline in f.readlines():
								fpath = None
								groupsA = re.findall(r'^(?:[^,]+,){3}\s*(\/.*?\/\/.*\S)\s*$',rline)
								groupsB = re.findall(r'^((?:[^,]+,){3})\s*\/.*?\/\/.*\S\s*$',rline)
								fpath = groupsA[0]
								fdeets = groupsB[0]

								if re.match(r'^\/masterpath\/',fpath):
									groups1 = re.findall(r'^\/masterpath\/(.*?)\/\/.*$',fpath)
									groups2 = re.findall(r'^\/masterpath\/.*?\/\/(.*)$',fpath)
									testgroupname=groups1[0]
									testrelativepath=groups2[0]
									if setname != testgroupname:
										continue
									testfullpath = targetpath+'/'+testrelativepath
								else:
									groups = re.findall(r'^(\/.*?)\/\/.*$',fpath)
									testgrouppath=groups[0]
									testgrouppath = testgrouppath.rstrip('/')
									testgrouppath = testgrouppath+'/'
									if testgrouppath != targetpath:
										continue
									testfullpath = fpath

								filelog.write(fdeets+testfullpath+'\n')

						filelog.close()
						f.close()


						loglist.append({'log':logname,'path':targetpath,'setname':setname,'sourcename':sourcename})
						logset[groupname][setname][sourcename]=logname
						masterpath=logpath+'master/';	#	md5vali-master-
						mastset[groupname]=masterpath


	elif 'foldersets' in infosets.keys():
		for setname,folderset in infosets['foldersets'].iteritems():
			for sourcename,folderpath in folderset.iteritems():
				if setname not in logset[groupname].keys():
					logset[groupname][setname]={}

				if sourcename not in foundlist.keys():
					continue
				startpath=foundlist[sourcename]

				logname= logpath+'pieces/'+sourcename+'/'+setname+'/md5vali-'+sourcename+'-'+timestr+'.txt'

				driveutils.createNewLog(logname,False)
				targetpath = startpath+folderpath
				targetpath = targetpath.replace('//','/')
				targetpath = targetpath.rstrip('/')
				targetpath = targetpath+'/'
				###### str replace // to /.  rstrip /. add /? (test each way)

				filelist.beginMD5Walk(targetpath,logname,md5opts['walkopts'])

				if '_errs' in md5opts['walkopts'].keys():
					if '_folders' in md5opts['walkopts']['_errs'].keys():
						if 'folderload' not in errset.keys():
							errset['folderload']={}
						if setname not in errset['folderload'].keys():
							errset['folderload'][setname]={}
						if sourcename not in errset['folderload'][setname].keys():
							errset['folderload'][setname][sourcename]=[]
						errset['folderload'][setname][sourcename].extend(md5opts['walkopts']['_errs']['_folders'])

				loglist.append({'log':logname,'path':targetpath,'setname':setname,'sourcename':sourcename})
				logset[groupname][setname][sourcename]=logname
				masterpath=logpath+'master/';	#	md5vali-master-
#				logset[name][setname]['master']=masterpath
				mastset[groupname]=masterpath

#				print '---- b',setname,sourcename,startpath,logname
#				print '---- c',setname,sourcename,masterpath
#	return {}

	print
	print ' -- saved logs -- '
	for log in loglist:
		print log['log']
	print

	for log in loglist:
		comparedata.sortLogByPath(log['log'])

	newdata={}
	newdata['timestr'] = timestr
	newdata['logset'] = logset
	newdata['mastset'] = mastset
	newdata['loglist'] = loglist
	newdata['errset'] = errset
	if 'foldersets' in infosets.keys():
		newdata['targets'] = infosets['foldersets']

	return newdata

def splitMasterLog(masterlog,logfolder,runname,timestamp):
	logpath = logfolder+'/md5vali/'+runname+'/';
	logpath += 'sections/'

	masterpieces={}
	with open(masterlog) as masterfile:
	    for rline in masterfile.readlines():
			fpath = None
			groupsA = re.findall(r'^(?:[^,]+,){3}\s*(\/.*?\/\/.*\S)\s*$',rline)
			groupsB = re.findall(r'^((?:[^,]+,){3})\s*\/.*?\/\/.*\S\s*$',rline)
			fpath = groupsA[0]
			fdeets = groupsB[0]

			if re.match(r'^\/masterpath\/',fpath):
				groups1 = re.findall(r'^\/masterpath\/(.*?)\/\/.*$',fpath)
				setname=groups1[0]

				logpiece = logpath+'/'+setname+'/masterpiece.txt'

				if not os.path.exists(logpiece):
					driveutils.createNewLog(logpiece,True)

				if setname not in masterpieces.keys():
					masterpieces[setname]={}
				if 'path' not in masterpieces[setname].keys():
					masterpieces[setname]['path']=logpiece
				if 'obj' not in masterpieces[setname].keys():
					masterpieces[setname]['obj']=open(logpiece,"a")

				masterpieces[setname]['obj'].write(rline)

	masterfile.close()

	for setname,mast in masterpieces.iteritems():
		if 'obj' in masterpieces[setname].keys():
			masterpieces[setname]['obj'].close()
			del masterpieces[setname]['obj']

	return masterpieces




def md5SourcesAndTargets(targetlist,logfolder,datasets,md5opts=None):
	if md5opts is None:
		md5opts={}
	if 'compopts' not in md5opts.keys():
		md5opts['compopts']={}

	for runname,loglist in datasets['logset'].iteritems():

		masterroute = datasets['mastset'][runname]

		if 'usemd5log' in md5opts['compopts'].keys() and 'logpath' in md5opts['compopts']['usemd5log'].keys():
			masterlog=md5opts['compopts']['usemd5log']['logpath']
		else:
			masterlog=grabAMasterLog(masterroute,datasets['timestr'],md5opts['compopts'])
		masterlogset=splitMasterLog(masterlog,logfolder,runname,datasets['timestr'])

		if runname in datasets['mastset'].keys():
			print '========================================='
			comparedata.beginCompareStage(loglist,runname,masterlogset,datasets['mastset'][runname],datasets['timestr'],targetlist,datasets,md5opts['compopts'])

def logAndCompTargets(targetlist, logfolder, md5opts=None):
	if md5opts is None:
		md5opts={}

	timestr = time.strftime("%Y%m%d-%H%M%S")
	mountlist = findmounts.getMounts()

	for groupname,infosets in targetlist.iteritems():
		if 'file' in infosets.keys():
			foundlist = findmounts.findTargetsInMounts(mountlist, infosets['file'])


		fake = 0
#		fake = 1
		if fake is None or fake == 0:
			tmplogs.clearTmpMD5Logs('md5vali',groupname,logfolder)
			datasets = createNewTmpMD5Logs(groupname,timestr,infosets,foundlist,logfolder,md5opts)

		if fake is not None and fake == 1:
			groupname='gmac_backup'
			timestrF = "20170622-160958"
			logpath = logfolder+'/md5vali/'+groupname+'/';
			md5opts['compopts']['dropold']=True
			if 'askdropold' in md5opts['compopts'].keys():
				del md5opts['compopts']['askdropold']

			testfolder=logpath+'master/master-'+timestrF+'/'
			testfile=logpath+'master/md5vali-summary-'+timestrF+'.txt'
			if os.path.exists(testfolder) and not os.path.isfile(testfolder):
				shutil.rmtree(testfolder)
			if os.path.exists(testfile) and os.path.isfile(testfile):
				os.remove(testfile)

			fakesets={'efset1':{},'efset2':{},'efset3':{},'efset4':{}}
			fakesets['efset1']['source']='/media/fileserver/fdrive/Multimedia'
			fakesets['efset1']['target1']='/media/backup/fileserver/fdrive/Multimedia'
			fakesets['efset2']['source']='/media/fileserver/fdrive/My Music'
			fakesets['efset2']['target1']='/media/backup/fileserver/fdrive/My Music'
			fakesets['efset3']['source']='/media/fileserver/fdrive/My Documents/My Pictures'
			fakesets['efset3']['target1']='/media/backup/fileserver/fdrive/My Documents/My Pictures'
			fakesets['efset4']['source']='/media/fileserver/fdrive/My Documents/Downloads'
			fakesets['efset4']['target1']='/media/backup/fileserver/fdrive/My Documents/Downloads'
			loglist=[]
			logset={}
			mastset={}
			for setname,folderset in fakesets.iteritems():
				driveutils.createDictSet(logset,[groupname,setname])
	#			print '--','foldersets',setname
				for sourcename,folderpath in folderset.iteritems():
					startpath=foundlist[sourcename]

					logname= logpath+'pieces/'+sourcename+'/'+setname+'/md5vali-'+sourcename+'-'+timestrF+'.txt'
					loglist.append({'log':logname,'path':startpath+folderpath,'setname':setname,'sourcename':sourcename})
					logset[groupname][setname][sourcename]=logname
					masterpath=logpath+'master/';	#	md5vali-master-
	#				logset[name][setname]['master']=masterpath
					mastset[groupname]=masterpath
			newdata={}
			newdata['timestr'] = timestrF
			newdata['logset'] = logset
			newdata['mastset'] = mastset
			newdata['loglist'] = loglist
			newdata['errset'] = {}
			if 'foldersets' in infosets.keys():
				newdata['targets'] = fakesets
			datasets=newdata


		if len(datasets.keys()) > 0:
			datasets['found']=foundlist

			md5SourcesAndTargets(targetlist,logfolder,datasets,md5opts)

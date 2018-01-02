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
#	print infosets.keys()
	if 'foldersets' in infosets.keys():
		for setname,folderset in infosets['foldersets'].iteritems():
#			print '--','foldersets',setname
			for sourcename,folderpath in folderset.iteritems():
#				print '----',setname,sourcename,folderpath
				if setname not in logset[groupname].keys():
#					print 'new',logset[groupname].keys()
					logset[groupname][setname]={}

#				print '---- a',setname,sourcename,foundlist.keys()
				if sourcename not in foundlist.keys():
					continue
				startpath=foundlist[sourcename]

				logname= logpath+'pieces/'+sourcename+'/'+setname+'/md5vali-'+sourcename+'-'+timestr+'.txt'

				driveutils.createNewLog(logname,False)
				piecepath = startpath+folderpath
				piecepath = piecepath.replace('//','/')
				piecepath = piecepath.rstrip('/')
				piecepath = piecepath+'/'
				###### str replace // to /.  rstrip /. add /? (test each way)

				filelist.beginMD5Walk(piecepath,logname,md5opts['walkopts'])

				if '_errs' in md5opts['walkopts'].keys():
					if '_folders' in md5opts['walkopts']['_errs'].keys():
						if 'folderload' not in errset.keys():
							errset['folderload']={}
						if setname not in errset['folderload'].keys():
							errset['folderload'][setname]={}
						if sourcename not in errset['folderload'][setname].keys():
							errset['folderload'][setname][sourcename]=[]
						errset['folderload'][setname][sourcename].extend(md5opts['walkopts']['_errs']['_folders'])

				loglist.append({'log':logname,'path':piecepath,'setname':setname})
				logset[groupname][setname][sourcename]=logname
				masterpath=logpath+'master/';	#	md5vali-master-
#				logset[name][setname]['master']=masterpath
				mastset[groupname]=masterpath

#				print '---- b',setname,sourcename,startpath,logname
#				print '---- c',setname,sourcename,masterpath

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

def md5SourcesAndTargets(targetlist,logfolder,datasets,md5opts=None):
	if md5opts is None:
		md5opts={}
	if 'compopts' not in md5opts.keys():
		md5opts['compopts']={}

	for runname,loglist in datasets['logset'].iteritems():
#		print
#		print 'xxxxxxxxxxxxxxx',runname
#		print targetlist[runname].keys(),targetlist[runname]
		if runname in datasets['mastset'].keys():
#			infoset={}
#			infoset['matchingsets']={}
#			infoset['matchingsets']

#			print loglist,runname, datasets['mastset'][runname]
#			print datasets['timestr'],datasets.keys(),md5opts['compopts']
#			print
			comparedata.beginCompareStage(loglist,runname,datasets['mastset'][runname],datasets['timestr'],targetlist,datasets,md5opts['compopts'])

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
					loglist.append({'log':logname,'path':startpath+folderpath,'setname':setname})
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


		datasets['found']=foundlist


		md5SourcesAndTargets(targetlist,logfolder,datasets,md5opts)

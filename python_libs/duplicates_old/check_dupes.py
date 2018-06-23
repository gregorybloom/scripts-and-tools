from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv


def concatTmpLogGroups(concatarr,newlogname):
	driveutils.createNewLog(newlogname,False)
	newlog = open(newlogname, 'ab')

	for logitem in concatarr:
		if os.path.exists(logitem) and os.path.isfile(logitem):
			flogobj = open(logitem, 'r')
			for line in flogobj:
				newlog.write(line)
			flogobj.close()
	newlog.close()

def createNewTmpMD5Logs(logtype,groupname,timestr,foldersets,foundlist,logfolder,md5opts=None):
	driveutils.createDictSet(md5opts,['walkopts'])

	logset={}
	mastset={}
	errset={}
	loglist=[]

	logpath = logfolder+'/'+logtype+'/'+groupname+'/';
	for setname,folderset in foldersets.iteritems():
		for sourcename,folderpath in folderset.iteritems():
			driveutils.createDictSet(logset,[groupname,setname])

			if sourcename not in foundlist.keys():
				continue
			startpath=foundlist[sourcename]

			logname= logpath+'pieces/'+setname+'/'+sourcename+'/'+logtype+'-'+setname+'-'+timestr+'.txt'

			driveutils.createNewLog(logname,False)

			filelist.beginMD5Walk(startpath+folderpath,logname,md5opts['walkopts'])

			if '_errs' in md5opts['walkopts'].keys():
				if '_folders' in md5opts['walkopts']['_errs'].keys():
					if 'folderload' not in errset.keys():
						errset['folderload']={}
					if setname not in errset['folderload'].keys():
						errset['folderload'][setname]={}
					if sourcename not in errset['folderload'][setname].keys():
						errset['folderload'][setname][sourcename]=[]
					errset['folderload'][setname][sourcename].extend(md5opts['walkopts']['_errs']['_folders'])

#			loglist.append({'log':logname,'path':startpath+folderpath,'setname':setname})
			logset[groupname][setname][sourcename]=logname
			masterpath=logpath+'master/';	#	md5vali-master-
#			logset[name][setname]['master']=masterpath
			mastset[groupname]=masterpath

	for setname,folderset in foldersets.iteritems():
		concatarr=[]
		for sourcename,folderpath in folderset.iteritems():
			logname=logpath+'pieces/'+setname+'/'+sourcename+'/'+logtype+'-'+setname+'-'+timestr+'.txt'
			if os.path.exists(logname) and os.path.isfile(logname):
				concatarr.append(logname)

		newlogname=logpath+'parts/'+setname+'/'+logtype+'-'+setname+'-'+timestr+'.txt'
		concatTmpLogGroups(concatarr,newlogname)
		loglist.append({'log':newlogname,'path':startpath+folderpath,'setname':setname})
	print
	print ' -- saved logs -- '
	for log in loglist:
		print log['log']
	print

	for log in loglist:
		comparedupes.sortLogBySHA(log['log'])

	newdata={}
	newdata['timestr'] = timestr
	newdata['logset'] = logset
	newdata['mastset'] = mastset
	newdata['loglist'] = loglist
	newdata['errset'] = errset
	newdata['targets'] = foldersets

	return newdata

def searchLogs(targetlist,runname,logfolder,datasets,md5opts=None):
	driveutils.createDictSet(md5opts,['compopts'])

	print

	print runname
	print logfolder
	print datasets['mastset'][runname]
	print datasets['timestr']
	print targetlist
	print datasets
	print md5opts['compopts']

	if runname in datasets['mastset'].keys():
		comparedupes.beginCompareStage(datasets['loglist'],runname,logfolder,datasets['mastset'][runname],datasets['timestr'],targetlist,datasets,md5opts['compopts'])

def findDuplicates(targetlist, logfolder, md5opts=None):
	timestr = time.strftime("%Y%m%d-%H%M%S")

	mountlist = findmounts.getMounts()
	for runname,infosets in targetlist.iteritems():
		if 'file' in infosets.keys():
			foundlist = findmounts.findTargetsInMounts(mountlist, infosets['file'])

		tmplogs.clearTmpMD5Logs('md5dupes',runname,logfolder)
		for i,data in infosets.iteritems():
			print '-',i,' > ',data

		datasets = {}
		if 'foldersets' in infosets.keys():
			datasets = createNewTmpMD5Logs('md5dupes',runname,timestr,infosets['foldersets'],foundlist,logfolder,md5opts)

		for i,data in datasets.iteritems():
			print i,' : ',data

		datasets['found']=foundlist

		searchLogs(targetlist,runname,logfolder,datasets,md5opts)

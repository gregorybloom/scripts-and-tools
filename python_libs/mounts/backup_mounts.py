from maintenance_loader import *

import os, sys, hashlib, time, re

def buildSetsFromFolderlists(source,target):
	sets = []
	if 'folderlist' in target.keys() and 'folderlist' in source.keys():
		c=0
		while c<len(target['folderlist']) or c<len(source['folderlist']):
			newset={}
			d=min(c,len(source['folderlist']))
			newset['source']=source['folderlist'][d]
			e=min(c,len(target['folderlist']))
			newset['path']=target['folderlist'][e]

			sets.append(newset)
			c=c+1
	return sets

def buildLogpath(pathopts,name,backuplist,pathtype="md5"):
	timestr = time.strftime("%Y%m%d-%H%M%S")

	logpath=""
	if 'mount' in pathopts.keys():
		logpath = backuplist[ pathopts['mount'] ]

	if 'path' in pathopts.keys():
		logpath = logpath + pathopts['path']
	else:
		if pathtype == "copy":
			logpath = logpath +'/logs/copylog/copylog-'+name+'-'+timestr+'.txt'
		if pathtype == "md5":
			logpath = logpath +'/logs/copylog/copylog-'+name+'-'+timestr+'.txt'

	if re.match(".*\[timestamp\.*",logpath):
		logpath = re.sub("\[timestamp\]",timestr,logpath)
	return logpath

def backupSourcesToTargets(backuplist,foldersets,copyopts):
	def makePathObject(pathname,backuplist,foldersets):
		pathobj={}
		pathobj['mount']=backuplist[pathname]
		pathobj['folderlist']=[]
		for fgroup,ftarget in foldersets.iteritems():
			if pathname in ftarget.keys():
				pathobj['folderlist'].append( pathobj['mount'] + ftarget[pathname])
		return pathobj

	if 'source' not in backuplist.keys():
		return

	sourceobj = makePathObject('source',backuplist,foldersets)
	for name,target in backuplist.iteritems():
		if name == 'source':
			continue
		else:
			targetobj = makePathObject(name,backuplist,foldersets)
#			print sourceobj,targetobj
			sets = buildSetsFromFolderlists(sourceobj,targetobj)
#			print sets

			logpath=None
			if 'logpath' in copyopts.keys():
				logpath = buildLogpath(copyopts['logpath'],name,backuplist,"copy")

			walknotes={}
			print logpath
#			return
			for group in sets:
				print
				print group['source'], ' copied to ', group['path']
				copydrive.beginCopyDrive( group['source'], group['path'], logpath, copyopts, walknotes, True  )

#			for group in sets:
#				print
			copydrive.beginResolveErrs(group['source'], group['path'], logpath, copyopts, walknotes, True )

			print ' - logged in: ', logpath

def logMD5sAtTargets(backuplist, logopts=None):
	if logopts is None:
		logopts={}
	if 'walkopts' not in logopts.keys():
		logopts['walkopts']={}

	for name,target in backuplist.iteritems():
#		if name == 'source':
#			continue
		if 'mount' in target:
			sets = buildSetsFromFolderlists(backuplist['source'],target)
			logpath=None
			if 'logpath' in logopts.keys():
				logpath = buildLogpath(logopts['logpath'],name,backuplist,"copy")

			for group in sets:
				filelist.beginMD5Walk(group['path'],logpath,logopts['walkopts'])
#				if switches['target']=='path':
#				filelist.beginFileList( group['path'], '', logpath, True  )
#				elif switches['target']=='source':
#					filelist.beginFileList( group['source'], '', logpath, True  )

			print ' - logged in: ', logpath
########################################################################
def backupByTargets(targetlist, opts=None):
	if opts is None:
		opts={}
#	sourcepath = ''


	timestr = time.strftime("%Y%m%d-%H%M%S")
	mountlist = findmounts.getMounts()
	for groupname,infosets in targetlist.iteritems():
		if 'file' in infosets.keys():
			foundlist = findmounts.findTargetsInMounts(mountlist, infosets['file'])

			for backupname,backuplist in foundlist.iteritems():
				print backupname,backuplist
			backupSourcesToTargets(foundlist,infosets['foldersets'],opts['copyopts'])
#		for groupname,groupinfo in backuplist.iteritems():
#			return
#			if 'md5log' in opts:
#				logMD5sAtTargets(backuplist,opts['md5logopts'])
		else:
			print 'ERROR, mount:',infosets,' not found!'

#	mountlist = findmounts.getMounts()

#	findmounts.findTargetsInMounts(mountlist, targetlist)
#	for backupname,backuplist in targetlist.iteritems():
#		for groupname,groupinfo in backuplist.iteritems():
#			print groupname,groupinfo
#			if 'mount' not in groupinfo.keys():
#				print 'ERROR, mount:',groupinfo['file'],' not found!'
#				exit()

##	for backupname,backuplist in targetlist.iteritems():
##		print backupname,backuplist
##		if 'source' in backuplist.keys():
##			if 'mount' in backuplist['source'].keys():
##				sourcepath = backuplist['source']['mount']
##			if sourcepath == '':
##				exit()
#
#		backupSourcesToTargets(backuplist,opts['copyopts'])
#		return
#		if 'md5log' in opts:
#			logMD5sAtTargets(backuplist,opts['md5logopts'])

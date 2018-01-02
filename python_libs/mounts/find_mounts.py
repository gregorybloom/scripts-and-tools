from maintenance_loader import *

import os, sys, hashlib, time


def getMounts():
	mountarr = driveutils.executeMountProcess()
#	mountarr = driveutils.executeProcess('mount')
	mountstr = ''.join(mountarr)
	mountarr = mountstr.split('\n')
	c=1
	while c>0:
		c=0
		for mount in mountarr:
			if( len(mount) < 1 ):
				mountarr.remove(mount)
	returnarr=[]
	for mount in mountarr:
		arr = mount.split(" ")
		arr[0]=arr[0].strip(":")
		returnarr.append( [ arr[0], arr[2], arr[4] ] )
	return returnarr

def findTargetsInMounts(mountlist, targetlist):
	foundlist={}
	for mount in mountlist:
		readlist = driveutils.readDir( mount[1] )
#		for backupname,backuplist in targetlist.iteritems():
#			for groupname,groupinfo in backuplist.iteritems():
#				if 'file' in groupinfo.keys():
#		print '1',mount,readlist
		for groupname,groupinfo in targetlist.iteritems():
			for read in readlist:
#				print '2',groupname,groupinfo['file'],'==',read
				if read == groupinfo:
					foundlist[groupname]=mount[1]

#							print '-', groupname, mount[1], ':',read, '==',groupinfo['file']
#					groupinfo['name'] = mount[2]
#					groupinfo['mount'] = mount[1]
#					if 'folderlist' in groupinfo.keys():
#						for c in range(0, len(groupinfo['folderlist'])):
#							groupinfo['folderlist'][c] = groupinfo['mount']+groupinfo['folderlist'][c]
					break
	return foundlist


def findTargetsInMountsOLD(mountlist, targetlist):
	for mount in mountlist:
		readlist = driveutils.readDir( mount[1] )
		for name,target in targetlist.iteritems():
			for read in readlist:
#				print '-', name, mount[1], ':',read, '==',target['file']
				if read == target['file']:
					target['name'] = mount[2]
					if 'path' in target:
						target['path'] = mount[1]+target['path']
#						print name,target['path']
					if 'sets' in target:
						for path in target['sets']:
							if 'path' in path:
								path['path'] = mount[1]+path['path']
#								print name,path['path']
					target['mount'] = mount[1]
					break
	return targetlist

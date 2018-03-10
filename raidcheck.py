from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv


targetList={}
targetList['raid_backup']={}

targetList['raid_backup']={'file':{},'foldersets':{},'subinfo':{}}




targetList['raid_backup']['file']['source']='_DRIVEFLAG_THE_RAID_.txt'
arglist=sys.argv[1:]
if "manuback" in arglist:
	targetList['raid_backup']['file']['target3']='_DRIVEFLAG_RAID_BACKUP2_DATA_.txt'
	targetList['raid_backup']['file']['target4']='_DRIVEFLAG_RAID_BACKUP2_VIDEO_.txt'
if "autoback" in arglist:
	targetList['raid_backup']['file']['target1']='_DRIVEFLAG_RAID_BACKUP_DATA_.txt'
	targetList['raid_backup']['file']['target2']='_DRIVEFLAG_RAID_BACKUP_VIDEO_.txt'


for name in targetList['raid_backup']['file']:
	targetList['raid_backup']['subinfo'][name]={}

targetList['raid_backup']['foldersets']={}

targetList['raid_backup']['foldersets']['videoset']={}
targetList['raid_backup']['foldersets']['videoset']['source']='/Media/Videos'
targetList['raid_backup']['foldersets']['videoset']['target2']='/RAID_BACKUP/Media/Videos'
targetList['raid_backup']['foldersets']['videoset']['target4']='/RAID_BACKUP/Media/Videos'


targetList['raid_backup']['foldersets']['cloudset']={}
targetList['raid_backup']['foldersets']['cloudset']['source']='/CLOUD_BACKUP'
targetList['raid_backup']['foldersets']['cloudset']['target1']='/RAID_BACKUP/CLOUD_BACKUP'
targetList['raid_backup']['foldersets']['cloudset']['target3']='/RAID_BACKUP/CLOUD_BACKUP'
targetList['raid_backup']['foldersets']['dataset']={}
targetList['raid_backup']['foldersets']['dataset']['source']='/Data'
targetList['raid_backup']['foldersets']['dataset']['target1']='/RAID_BACKUP/Data'
targetList['raid_backup']['foldersets']['dataset']['target3']='/RAID_BACKUP/Data'
targetList['raid_backup']['foldersets']['miscset']={}
targetList['raid_backup']['foldersets']['miscset']['source']='/Misc'
targetList['raid_backup']['foldersets']['miscset']['target1']='/RAID_BACKUP/Misc'
targetList['raid_backup']['foldersets']['miscset']['target3']='/RAID_BACKUP/Misc'
targetList['raid_backup']['foldersets']['projset']={}
targetList['raid_backup']['foldersets']['projset']['source']='/Projects'
targetList['raid_backup']['foldersets']['projset']['target1']='/RAID_BACKUP/Projects'
targetList['raid_backup']['foldersets']['projset']['target3']='/RAID_BACKUP/Projects'
targetList['raid_backup']['foldersets']['servscriptset']={}
targetList['raid_backup']['foldersets']['servscriptset']['source']='/SERVER_SCRIPTS'
targetList['raid_backup']['foldersets']['servscriptset']['target1']='/RAID_BACKUP/SERVER_SCRIPTS'
targetList['raid_backup']['foldersets']['servscriptset']['target3']='/RAID_BACKUP/SERVER_SCRIPTS'
targetList['raid_backup']['foldersets']['sidedriveset']={}
targetList['raid_backup']['foldersets']['sidedriveset']['source']='/SIDE_DRIVES'
targetList['raid_backup']['foldersets']['sidedriveset']['target1']='/RAID_BACKUP/SIDE_DRIVES'
targetList['raid_backup']['foldersets']['sidedriveset']['target3']='/RAID_BACKUP/SIDE_DRIVES'
targetList['raid_backup']['foldersets']['softset']={}
targetList['raid_backup']['foldersets']['softset']['source']='/Software'
targetList['raid_backup']['foldersets']['softset']['target1']='/RAID_BACKUP/Software'
targetList['raid_backup']['foldersets']['softset']['target3']='/RAID_BACKUP/Software'
targetList['raid_backup']['foldersets']['spiderdumpset']={}
targetList['raid_backup']['foldersets']['spiderdumpset']['source']='/SPIDER_DUMP'
targetList['raid_backup']['foldersets']['spiderdumpset']['target1']='/RAID_BACKUP/SPIDER_DUMP'
targetList['raid_backup']['foldersets']['spiderdumpset']['target3']='/RAID_BACKUP/SPIDER_DUMP'
targetList['raid_backup']['foldersets']['m_bookset']={}
targetList['raid_backup']['foldersets']['m_bookset']['source']='/Media/Books'
targetList['raid_backup']['foldersets']['m_bookset']['target1']='/RAID_BACKUP/Media/Books'
targetList['raid_backup']['foldersets']['m_bookset']['target3']='/RAID_BACKUP/Media/Books'
targetList['raid_backup']['foldersets']['m_comicset']={}
targetList['raid_backup']['foldersets']['m_comicset']['source']='/Media/Comics'
targetList['raid_backup']['foldersets']['m_comicset']['target1']='/RAID_BACKUP/Media/Comics'
targetList['raid_backup']['foldersets']['m_comicset']['target3']='/RAID_BACKUP/Media/Comics'
targetList['raid_backup']['foldersets']['m_imageset']={}
targetList['raid_backup']['foldersets']['m_imageset']['source']='/Media/Images'
targetList['raid_backup']['foldersets']['m_imageset']['target1']='/RAID_BACKUP/Media/Images'
targetList['raid_backup']['foldersets']['m_imageset']['target3']='/RAID_BACKUP/Media/Images'
targetList['raid_backup']['foldersets']['m_musicset']={}
targetList['raid_backup']['foldersets']['m_musicset']['source']='/Media/Music'
targetList['raid_backup']['foldersets']['m_musicset']['target1']='/RAID_BACKUP/Media/Music'
targetList['raid_backup']['foldersets']['m_musicset']['target3']='/RAID_BACKUP/Media/Music'
targetList['raid_backup']['foldersets']['m_recordingset']={}
targetList['raid_backup']['foldersets']['m_recordingset']['source']='/Media/Recordings'
targetList['raid_backup']['foldersets']['m_recordingset']['target1']='/RAID_BACKUP/Media/Recordings'
targetList['raid_backup']['foldersets']['m_recordingset']['target3']='/RAID_BACKUP/Media/Recordings'
targetList['raid_backup']['foldersets']['m_unsortedset']={}
targetList['raid_backup']['foldersets']['m_unsortedset']['source']='/Media/-unsorted'
targetList['raid_backup']['foldersets']['m_unsortedset']['target1']='/RAID_BACKUP/Media/-unsorted'
targetList['raid_backup']['foldersets']['m_unsortedset']['target3']='/RAID_BACKUP/Media/-unsorted'


do_only=['servscriptset','miscset','m_recordingset','videoset']
do_only=['m_recordingset']
for k in targetList['raid_backup']['foldersets'].keys():
	if k not in do_only:
#		continue
		del targetList['raid_backup']['foldersets'][k]



runopts={}
runopts['walkopts']={}
runopts['compopts']={}
runopts['walkopts']['numthreads']=2
#runopts['walkopts']['printon']=10


if "_printon" in arglist:
	pt=arglist.index("_printon")+1
	if pt < len(arglist):
		runopts['walkopts']['printon']=int(arglist[pt])


runopts['walkopts']['filters']={'deny':["garbage"],'allowonly':["imgs","videos","docs","zip","music","misc"]}

if "_testfromlog" in arglist:
	pt=arglist.index("_testfromlog")+1
	if pt < len(arglist):
		runopts['compopts']['useold_md5log']={'logpath':arglist[pt]}
if "_testatlog" in arglist:
	pt=arglist.index("_testatlog")+1
	if pt < len(arglist):
		runopts['walkopts']['usenew_md5log']={'logpath':arglist[pt],'setsource':'source'}
if "_outputatlog" in arglist:
	pt=arglist.index("_outputatlog")+1
	if pt < len(arglist):
		runopts['compopts']['useoutputlog']={'logpath':arglist[pt]}


if "verbose" in arglist:
	runopts['compopts']['verbose']=True
if "dropold" in arglist:
	runopts['compopts']['justdropmissing']=True

if "skipmovecheck" in arglist:
	runopts['compopts']['skipmovecheck']=True

logfolder="/var/log/validates"
tmpfolder="/tmp/validates"
checkmd5s.logAndCompTargets(targetList,logfolder,tmpfolder,runopts)

#	https://askubuntu.com/questions/380238/how-to-clean-tmp
#	find /tmp -ctime +10 -exec rm -rf {} +

#	sed -i -e 's/\/\/\//\/\//g' testfn.txt
#	for i in $(grep -inrlP "\/\/\/" /var/log/validates/md5vali/raid_backup/master/); do echo "$i" | grep -P "\-master\-" >> fixlist.txt; done
#	for i in $(cat fixlist.txt); do echo "----------" >> fixrun.txt; echo "$i" >> fixrun.txt; tail -n 2 "$i" >> fixrun.txt; sudo sed -i -e 's/\/\/\//\/\//g' "$i"; tail -n 2 "$i" >> fixrun.txt; done

###	/etc/fstab			-- scan/parse this for mounted info

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
do_only=['miscset','m_recordingset','m_bookset','cloudset']
do_only=['m_bookset']
for k in targetList['raid_backup']['foldersets'].keys():
	if k not in do_only:
		break
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
#runopts['walkopts']['method']={'slow':[],'fast':[]}

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


if "_readname" in arglist:
	pt=arglist.index("_readname")+1
	if pt < len(arglist):
		runopts['compopts']['readname']=arglist[pt]


if "verbose" in arglist:
	runopts['compopts']['verbose']=True
if "dropold" in arglist:
	runopts['compopts']['justdropmissing']=True


#if "skipmovecheck" in arglist:
#	runopts['compopts']['skipmovecheck']=True
if 'readname' not in runopts['compopts'].keys():
	runopts['compopts']['readname']="backuprun"
logfolder="/var/log/validates"
tmpfolder="/tmp/validates"




checkmd5s.logAndCompTargets(targetList,logfolder,tmpfolder,runopts)

#	https://askubuntu.com/questions/380238/how-to-clean-tmp
#	find /tmp -ctime +10 -exec rm -rf {} +

#	sed -i -e 's/\/\/\//\/\//g' testfn.txt
#	for i in $(grep -inrlP "\/\/\/" /var/log/validates/md5vali/raid_backup/master/); do echo "$i" | grep -P "\-master\-" >> fixlist.txt; done
#	for i in $(cat fixlist.txt); do echo "----------" >> fixrun.txt; echo "$i" >> fixrun.txt; tail -n 2 "$i" >> fixrun.txt; sudo sed -i -e 's/\/\/\//\/\//g' "$i"; tail -n 2 "$i" >> fixrun.txt; done

###	/etc/fstab			-- scan/parse this for mounted info

### resume a job, disowned
#  ctrl Z
#  jobs -l		# look for [jnum#] pid
#  bg <jnum#>
#  disown -h <jnum#>   # or -a for all.  or disown to affect all backgrounded processes


#	sudo rm /tmp/test_result.txt; sudo python raidcheck.py _readname "testrun" verbose _testfromlog "/var/log/validates/md5vali/backuprun/raid_backup/master/master-20180301-101210/md5vali-master-20180301-101210.txt" _testatlog "/tmp/validates/test_bookset.txt" >> /tmp/test_result.txt



#
#
#
#
'''
vee@edd:/media/raid/SERVER_SCRIPTS/scripts-and-tools$ grep -inrP "Sabbat" /var/log/validates/md5vali/backuprun/raid_backup/master/md5vali-summary-20180313-211712.txt
160:source - moved_fr, 96046e57b15bd65e526d2fb4247a9b35, 46237307, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
161:source - moved_to, 96046e57b15bd65e526d2fb4247a9b35, 46237307, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
163:source - moved_fr, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
164:source - moved_to, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
166:source - moved_fr, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
167:source - moved_to, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
169:source - moved_fr, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
170:source - moved_to, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
181:source - moved_fr, 96046e57b15bd65e526d2fb4247a9b35, 46237307, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
182:source - moved_to, 96046e57b15bd65e526d2fb4247a9b35, 46237307, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
184:source - moved_fr, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
185:source - moved_to, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
187:source - moved_fr, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
188:source - moved_to, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
190:source - moved_fr, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
191:source - moved_to, 65cc880bbf3c4ea70c12aa484307272e, 26443237, x,/media/raid/Media/Books//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf


vee@edd:/media/raid/SERVER_SCRIPTS/scripts-and-tools$ grep -inrP "Sabbat" /var/log/validates/md5vali/backuprun/raid_backup/master/master-20180301-101210/md5vali-master-20180301-101210.txt
#correct	103959:65cc880bbf3c4ea70c12aa484307272e, 26443237, Sun Nov  4 07:09:36 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
104060:53a613f72bae1f496d33ff4595b0fc04, 53497576, Tue Oct 30 12:20:28 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness (Old)/Vampire the Masquerade/Guide to the Sabbat (1999).pdf
104066:10a019d204b05572853b2e0a8dcc4056, 1163305, Sat Oct 27 04:22:08 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness (Old)/Vampire the Masquerade/Player's Guide to The Sabbat (1997).pdf
104090:96db30defe304eaa4b9c377cb33de4e4, 600086, Sat Oct 27 04:27:46 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness (Old)/Vampire the Masquerade/Storyteller's Handbook to The Sabbat (1992,1997).pdf
#correct	104498:65cc880bbf3c4ea70c12aa484307272e, 26443237, Sun Nov  4 07:09:36 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
104599:53a613f72bae1f496d33ff4595b0fc04, 53497576, Tue Oct 30 12:20:28 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness/Vampire the Masquerade/Guide to the Sabbat (1999).pdf
104605:10a019d204b05572853b2e0a8dcc4056, 1163305, Sat Oct 27 04:22:08 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness/Vampire the Masquerade/Player's Guide to The Sabbat (1997).pdf
104629:96db30defe304eaa4b9c377cb33de4e4, 600086, Sat Oct 27 04:27:46 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness/Vampire the Masquerade/Storyteller's Handbook to The Sabbat (1992,1997).pdf



----------------------------------------------
y   136293dd6121a85ce4274c996583aefe, 18716862, Tue Oct 30 12:55:08 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf

@  source 767253 /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf ['obj', 'cur_path', 'logpath', 'pos', 'line', 'cur_sha']
@  _oldmaster 877363 /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf ['obj', 'cur_path', 'logpath', 'pos', 'line', 'cur_sha']
s: /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf ['source', '_oldmaster']
found:  /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf
s% source present 136293dd6121a85ce4274c996583aefe /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf
s> pstate sPdPmP
s> masterstate present
s> totalstates {'_total': 1, 'present': 1}
s> groupstates {'present': ['source']}
s> overall present
s> compset ['_oldmaster', 'source']
s> sha 136293dd6121a85ce4274c996583aefe
s> sstate sSdSmS
s> path /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf
s> mastersha 136293dd6121a85ce4274c996583aefe
precheck # 5076 ! m_bookset, /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of Elysium (1998).pdf ! sPdPmP, sSdSmS, None
----------------------------------------------
----------------------------------------------
y   65cc880bbf3c4ea70c12aa484307272e, 26443237, Sun Nov  4 07:09:36 2012, /masterpath/m_bookset//RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf

@  source 767417 /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, revised (1999).pdf ['obj', 'cur_path', 'logpath', 'pos', 'line', 'cur_sha']
@  _oldmaster 877549 /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf ['obj', 'cur_path', 'logpath', 'pos', 'line', 'cur_sha']
s: /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf ['_oldmaster']
s: /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, revised (1999).pdf ['source']
found:  /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
s% source missing 96046e57b15bd65e526d2fb4247a9b35 /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, revised (1999).pdf
s> pstate sXdXmP
s> masterstate present
s> totalstates {'_total': 1, 'missing': 1}
s> groupstates {'missing': ['source']}
s> overall missing
s> compset ['_oldmaster']
s> sha 65cc880bbf3c4ea70c12aa484307272e
s> sstate sXdXmS
s> path /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf
s> mastersha 65cc880bbf3c4ea70c12aa484307272e
precheck # 5077 ! m_bookset, /RPGs/World of Darkness/World of Darkness (Old)/Mind's Eye Theatre/Laws of The Night, Sabbat Guide (2000).pdf ! sXdXmP, sXdXmS, None
----------------------------------------------
----------------------------------------------

'''

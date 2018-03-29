from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv, datetime



arglist=sys.argv[1:]

if len(arglist) < 2:
	sys.exit(0)
if len(arglist) > 3:
	sys.exit(0)


md5log=arglist[0]
resultlog=arglist[1]

tmpdir=None
if len(arglist) == 3:
	tmpdir=arglist[2]


starttime = datetime.datetime.now()

finddupes.buildALogOfDupes(md5log,resultlog,tmpdir)

endtime = datetime.datetime.now()

print "started: ",starttime
print "duration: ",(endtime-starttime)

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
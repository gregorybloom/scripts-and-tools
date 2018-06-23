from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv, datetime

runopts={}


arglist=sys.argv[1:]

if len(arglist) < 2:
	sys.exit(0)

md5log=arglist[0]
resultlog=arglist[1]

arglist.pop(0)
arglist.pop(0)

if len(arglist) > 0:
	if "tmpdir" in arglist:
		pt=arglist.index("tmpdir")+1
		if pt < len(arglist):
			runopts['tmpdir']=int(arglist[pt])
	if "skipfirst" in arglist:
		runopts['skipfirst']=True
	if "skipthisfirst" in arglist:
		pt=arglist.index("skipthisfirst")+1
		if pt < len(arglist):
			runopts['skipthisfirst']=int(arglist[pt])





starttime = datetime.datetime.now()

finddupes.buildALogOfDupes(md5log,resultlog,runopts)

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

from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv


logmode="finddupes"

arglist=sys.argv[1:]

runopts={}
if "_testfromlog" in arglist:
	# primary log to compare from
	pt=arglist.index("_testfromlog")+1
	if pt < len(arglist):
		runopts['testlog']=arglist[pt]
if "_testatlog" in arglist:
	# secondary dupe log to compare to
	pt=arglist.index("_testatlog")+1
	if pt < len(arglist):
		runopts['verslog']=arglist[pt]
if "_outputatlog" in arglist:
	pt=arglist.index("_outputatlog")+1
	if pt < len(arglist):
		runopts['outlog']=arglist[pt]

if "_logfrompath" in arglist:
	pt=arglist.index("_logfrompath")+1
	if pt < len(arglist):
		runopts['logfrompath']=arglist[pt]

if "build" in arglist:
	logmode="buildlog"
if "skipfirst" in arglist:
	runopts['skipfirst']=True
if "_skipfirstpath" in arglist:
	runopts['skipfirstpath']=True
	pt=arglist.index("_skipfirstpath")+1
	if pt < len(arglist):
		runopts['skipfirstpathregex']=arglist[pt]
if "flipfilter" in arglist:
	runopts['flipfilter']=True

if 'outlog' not in runopts.keys():
	runopts['outlog']='tmp/dupe_output.txt'


if logmode == "finddupes":

	if 'outlog' in runopts.keys() and 'testlog' in runopts.keys():
		finddupes.buildALogOfDupes(runopts['testlog'], runopts['outlog'], runopts)

		print "Dupe Log built: ",runopts['outlog']
elif logmode == "buildlog":

	if 'outlog' in runopts.keys() and 'logfrompath' in runopts.keys():
		runopts['walkopts']={}
		runopts['walkopts']['filters']={'deny':["garbage"]}

		if 'flipfilter' not in runopts.keys() or runopts['flipfilter'] == False:
			runopts['walkopts']['filters']['allowonly']=["imgs","videos","docs","zip","music","misc"]
		else:
			runopts['walkopts']['filters']['deny'].extend( ["imgs","videos","docs","zip","music","misc"] )

		targetpath = re.findall("(.*)\/*\s*$",runopts['logfrompath'])[0]

		logname = runopts['outlog']

		driveutils.createNewLog(logname,False)
		filelist.beginMD5Walk(targetpath+'/',logname,runopts['walkopts'])
		driveutils.sortLogByPath(logname)

		print "MD5/SHA Log built: ",logname

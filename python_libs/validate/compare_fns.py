
from maintenance_loader import *

import imp
SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
comparesearch = imp.load_source('comparesearch', SCRIPTPATH+'/python_libs/validate/compare_search.py')

import os, sys, hashlib, time, shutil, re
from sys import version_info



def closeUpFiles(filelist):
	for i,item in filelist.iteritems():
		if 'obj' in item.keys():
			item['obj'].close()
#				print 'closed: ',i

def loadStepList(steplist,useopts):
	for name,item in steplist.iteritems():
		if name == "_newmaster":
			continue
		logObj = steplist[name]['obj']

		if 'pos' in item.keys():
#				steplist[name]['pos']=logObj.tell()
			resetLogPos(steplist[name])
			aline=logObj.readline()
#				print '##',name,aline
#				if aline is None:
#					print "#!"
			steplist[name]['line']=aline
#			steplist[name]['isnew']=isnew
			if useopts['firstrun']:
				steplist[name]['isnew']=True

def prepStepListVals(steplist,readname,runname,logsetname,tmpfolder,datasets,useopts):
	for name,item in steplist.iteritems():
		if name == "_newmaster":
			continue
		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		regE1 = r'^\*+, \-?[0-9]+,'
		regE2 = r'^(?:\*|[0-9])+, \*+,'
		regE3 = r'^[A-Za-z0-9]+, -1,'

		if 'loadErr' in steplist[name].keys():
			del steplist[name]['loadErr']


		if 'line' in item.keys():
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
				print '  ~x ',name,steplist[name]['isnew'],item['line']
			if not steplist[name]['isnew']:
				if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
					print ' _OLD',name,steplist[name]
				groups = None
				if len(item['line']) > 1:
					Acompare = driveutils.decomposeFileLog(item['line'])
					groups = re.findall(r'\/(\/.*)$',Acompare['fullpath'])
				else:
					continue
				if groups[0] == steplist[name]['cur_path']:
#					steplist[name]['cur_sha']=Acompare['sha']
#					steplist[name]['cur_mtype']=Acompare['mtype']
#					steplist[name]['cur_bsize']=Acompare['bytesize']

#					steplist[name]['cur_path']=groups[0]

#					steplist[name]['hashes']={}
#					steplist[name]['hashes'][ Acompare['mtype'] ]=Acompare['sha']
					continue

			if re.search(reg,item['line']):
				l = item['line']
				Acompare = driveutils.decomposeFileLog(item['line'])

				if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
					print ' _NEW',name,steplist[name]
				if 'cur_sha' not in steplist[name].keys() or steplist[name]['cur_sha'] != Acompare['sha']:
					if 'hashes' not in steplist[name].keys():
						steplist[name]['hashes']={}
					elif Acompare['mtype'] not in steplist[name]['hashes'].keys():
						steplist[name]['hashes']={}
					elif steplist[name]['hashes'][ Acompare['mtype'] ] != Acompare['sha']:
						steplist[name]['hashes']={}

				steplist[name]['hashes'][ Acompare['mtype'] ]=Acompare['sha']

				steplist[name]['cur_sha']=Acompare['sha']
				steplist[name]['cur_mtype']=Acompare['mtype']
				steplist[name]['cur_bsize']=Acompare['bytesize']

				groups = re.findall(r'\/(\/.*)$',Acompare['fullpath'])
				steplist[name]['cur_path']=groups[0]

				steplist[name]['line']=l
			elif re.search(regE1,item['line']) or re.search(regE2,item['line']) or re.search(regE3,item['line']):
				l = item['line']
				Acompare = driveutils.decomposeFileLog(item['line'])

				if 'cur_sha' not in steplist[name].keys() or steplist[name]['cur_sha'] != Acompare['sha']:
					if 'hashes' not in steplist[name].keys():
						steplist[name]['hashes']={}
					elif Acompare['mtype'] not in steplist[name]['hashes'].keys():
						steplist[name]['hashes']={}
					elif steplist[name]['hashes'][ Acompare['mtype'] ] != Acompare['sha']:
						steplist[name]['hashes']={}

				steplist[name]['hashes'][ Acompare['mtype'] ]=Acompare['sha']

				steplist[name]['cur_sha']=Acompare['sha']
				steplist[name]['cur_mtype']=Acompare['mtype']
				steplist[name]['cur_bsize']=Acompare['bytesize']

				groups = re.findall(r'\/(\/.*)$',Acompare['fullpath'])
				steplist[name]['cur_path']=groups[0]
				steplist[name]['loadErr']=True
				steplist[name]['line']=l
			else:
#				print "########",name,item
				steplist[name]['cur_path']=None
				steplist[name]['cur_sha']=None
				steplist[name]['cur_mtype']=None
				steplist[name]['cur_bsize']=None
				steplist[name]['hashes']={}

			if steplist[name]['cur_mtype'] is not None:
				if steplist[name]['cur_mtype'] != useopts['mtype']:

					if useopts['compmode'] == "compare":
						if useopts['mtype'] not in steplist[name]['hashes'].keys():
							comparesearch.grabFromNewCalcs(steplist,name,readname,runname,logsetname,name,tmpfolder,useopts)

					if useopts['mtype'] not in steplist[name]['hashes'].keys():
						if name == '_oldmaster':
							basepath = grabBasePath(logsetname,'source',datasets)
						else:
							basepath = grabBasePath(logsetname,name,datasets)

						if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
							print ' GET new:',name,steplist[name]['isnew'],steplist[name]

						newline = redoDataFile(item['line'],logsetname,steplist[name]['cur_path'],basepath,steplist[name]['hashes'],useopts)

						if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
							print '  - after redo:',steplist[name]['hashes'].keys()
						Acompare = driveutils.decomposeFileLog(newline)
						steplist[name]['cur_sha']=Acompare['sha']
						steplist[name]['cur_mtype']=Acompare['mtype']
						steplist[name]['cur_bsize']=Acompare['bytesize']
						steplist[name]['line']=newline
						if Acompare['mtype'] not in steplist[name]['hashes'].keys():
							steplist[name]['hashes'][ Acompare['mtype'] ]=Acompare['sha']
					else:
						steplist[name]['cur_sha']=steplist[name]['hashes'][ useopts['mtype'] ]
						steplist[name]['cur_mtype']=useopts['mtype']


def grabBasePath(logsetname,localdrive,datasets):
	if logsetname in datasets['targets'].keys() and localdrive in datasets['targets'][logsetname].keys():
		grouppath=datasets['targets'][logsetname][localdrive]
	if localdrive in datasets['found'].keys():
		drivepath=datasets['found'][localdrive]
	if grouppath is not None and drivepath is not None:
		basepath=drivepath.rstrip('/')+"/"+grouppath.rstrip('/').lstrip('/')+"/"
	return basepath

def redoDataFile(logline,logsetname,relativePath,basePath,hashesdict,useopts):
	filedata=re.findall(r'^(\w+,\s*\d+,\s*\w[^,]*,\s*)\/',logline)[0]
	filepath=re.findall(r'^\w+,\s*\d+,\s*\w[^,]*,\s*(\/.*\S)\s*$',logline)[0]

	mopt='md5'
	if 'mtype' in useopts.keys():
		mopt=useopts['mtype']

	mcheck='md5'
#	if len(filedata.split(',')) >= 5:
#	if re.find(r'',filedata)
	mcheckdata=re.findall(r'^\w+,\s*\d+,\s*(\w[^,]*),\s*$',filedata)[0]
	mcheckdata=driveutils.decomposeFileLogItemData(mcheckdata)
	if 'mtype' in mcheckdata.keys():
		mcheck = mcheckdata['mtype']

	if mcheck == mopt:
		newline = filedata+filepath+"\n"
		return newline
	elif mcheck in hashesdict.keys() and mopt in hashesdict.keys():
		masdatabit1=re.findall(r'^\w+,(\s*\d+,)\s*\w[^,]*,\s*\/.*$',filedata)[0]
		masdatabit2=re.findall(r'^\w+,\s*\d+,\s*(\w[^,]*),\s*\/.*$',filedata)[0]
		mcheckdata['mtype']=mopt
		masdata=hashesdict[mopt]+', '+masdatabit1+', '+driveutils.rebuildFileLogItemData(mcheckdata)+', '
		newline = masdata+filepath+"\n"
		return newline
	else:
		localpath=relativePath.lstrip('/')
		#########################check if file exists in source, recalc data##############################
		dlpath = None
		masdata = None
		if basePath is not None:
			dlpath=basePath.rstrip('/')+"/"+localpath
		if dlpath is not None and os.path.isfile(dlpath):
			if mcheck in hashesdict.keys() and mopt in hashesdict.keys():
				infobjOld={}
				infobjOld['sha']=hashesdict[mcheck]
				infobjOld['bytesize']=re.findall(r'^\w+,\s*(\d+),.*$',filedata)[0]
			else:
				if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
					print '** getsha:getfile1 - ',hashesdict.keys(),mcheckdata,dlpath,mcheck,'(',mopt,')'
				infobjOld=driveutils.getFileInfo(dlpath,None,{'mtype':mcheck})
				hashesdict[mcheck]=infobjOld['sha']
			mcheck2=re.findall(r'^(\w+),\s*\d+,.*$',filedata)[0]
			mcheck3=re.findall(r'^\w+,\s*(\d+),.*$',filedata)[0]
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
				print '**          chk1 - ',infobjOld['sha'],mcheck2,infobjOld['bytesize'],mcheck3
			if infobjOld['sha'] == mcheck2 and infobjOld['bytesize'] == mcheck3:
				if mcheck in hashesdict.keys() and mopt in hashesdict.keys():
					mcheckdata['mtype']=mopt
					masdata=hashesdict[mopt]+", "+infobjOld['bytesize']+", "+driveutils.rebuildFileLogItemData(mcheckdata)+", "
				else:
					if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
						print '** getsha:getfile2 - ',mcheckdata,dlpath,mopt
					infobjNew=driveutils.getFileInfo(dlpath,None,{'mtype':mopt})
					hashesdict[mopt]=infobjNew['sha']
					masdata=re.findall(r'^(\w+,\s*\d+,\s*\w[^,]*,\s*)\/.*$',infobjNew['fulltext'])[0]

		if masdata is not None:
			newline = masdata+filepath+"\n"
			return newline
		else:
			newline = filedata+filepath+"\n"
			return newline

def pushMasterListToGroup(masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts=None):
	for name,item in masterlist.iteritems():
		if name == "_newmaster":
			continue

		logObj = masterlist[name]['obj']
#			print 't  ',name,item

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if 'line' in item.keys():
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
				print ' .y  ',item['line']
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
				print ' .x  ',name,masterlist[name]['hashes']
			while re.search(reg,item['line']):
#				if re.search(reg,item['line']):
				l = item['line']
#					print 'XXX',name,item['line'],masterlist.keys()

				Acompare = driveutils.decomposeFileLog(item['line'])
				masterlist[name]['line']=l

				groups = re.findall(r'\/masterpath\/(.*?)\/\/.*$',Acompare['fullpath'])
				groupname=groups[0]


				if groupname != logsetname:
					if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
						print '     .  . skip: ',groupname,'!=',logsetname,': ',Acompare['fullpath'].rstrip()
#						print 'skip: ',groupname, logsetname, name
					incrementListed(masterlist,[name],useopts)
					loadStepList(masterlist,useopts)
					prepStepListVals(masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)
				else:
#						print 'up: ',groupname, logsetname, masterlist.keys()
					loadStepList(masterlist,useopts)
					prepStepListVals(masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)
					break




def comparePathsInLogSet(matches,filelist,useopts):
	for sourcename,item in filelist.iteritems():
		if 'cur_path' in item.keys():
			curpath = item['cur_path']

			if curpath is not None:
				if curpath not in matches.keys():
					matches[curpath]=[]

				matches[curpath].append(sourcename)
	return matches


def findLowestPath(matches,useopts):
	lowest=None
	for n,item in matches.iteritems():
#			print '==',n,item
		if lowest is None:
			lowest=n
		elif lowest>n:
			lowest=n
#		print

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		print 'found lowest path: ',lowest

	return lowest



def buildCompSet(lowest,matches,compSET,masterlist,useopts):
	compSET['_oldmaster']={}

	compSET['_oldmaster']['state'] = 'missing'
	compSET['_oldmaster']['cur_path'] = lowest

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		print " &&&&",lowest,"_oldmaster:",masterlist["_oldmaster"].keys(),'==',masterlist["_oldmaster"]
	if 'cur_path' in masterlist["_oldmaster"].keys():
		if lowest == masterlist["_oldmaster"]["cur_path"]:
			compSET['_oldmaster']['state'] = 'present'
			compSET['_oldmaster']['line'] = masterlist["_oldmaster"]["line"]
			compSET['_oldmaster']['cur_path'] = masterlist["_oldmaster"]["cur_path"]

			compSET['_oldmaster']['cur_sha'] = masterlist["_oldmaster"]["cur_sha"]
			compSET['_oldmaster']['cur_bsize'] = masterlist["_oldmaster"]['cur_bsize']
			compSET['_oldmaster']['cur_mtype'] = masterlist["_oldmaster"]["cur_mtype"]
			compSET['_oldmaster']['cur_errs'] = []

##% _oldmaster {'obj': <open file '/drives/c/Users/kingf/logs//md5vali/dokko_backup/master/master-20170611-143943/md5vali-master-20170611-143943.txt', mode 'rb' at 0xffddaf40>, 'cur_path': '/Extensions/dhdgffkkebhmkfjojejmpbldmpobfkfo/4.2.7_0/_locales/ja/about.txt', 'logpath': '/drives/c/Users/kingf/logs//md5vali/dokko_backup/master/master-20170611-143943/md5vali-master-20170611-143943.txt', 'pos': 287186L, 'line': '41e5298bdb3b42d2cf195bc0b45debf44a90a32253a69b87a4834f5246165a46, 309, Sun Jun 11 12:58:29 2017, /masterpath/efset5//Extensions/dhdgffkkebhmkfjojejmpbldmpobfkfo/4.2.7_0/_locales/ja/about.txt\n', 'cur_sha': '41e5298bdb3b42d2cf195bc0b45debf44a90a32253a69b87a4834f5246165a46'}
def addToCompSet(lowest,matches,compSET,steplist,logsetname,datasets,useopts):
	compSET['_summary'] = {}
	compSET['_summary']['path'] = lowest
	if 'cur_sha' in compSET['_oldmaster'].keys():
		compSET['_summary']['sha'] = compSET['_oldmaster']['cur_sha']
		compSET['_summary']['bsize'] = compSET['_oldmaster']['cur_bsize']
		compSET['_summary']['mtype'] = compSET['_oldmaster']['cur_mtype']

	compSET['_sources']={}
	for sourcename,sourceobj in steplist.iteritems():
		compSET['_sources'][sourcename] = {}

		if 'cur_path' in sourceobj.keys():
			compSET['_sources'][sourcename]['cur_path'] = sourceobj['cur_path']
		if 'cur_sha' in sourceobj.keys():
			compSET['_sources'][sourcename]['cur_sha'] = sourceobj['cur_sha']
		if 'cur_bsize' in sourceobj.keys():
			compSET['_sources'][sourcename]['cur_bsize'] = sourceobj['cur_bsize']
		if 'cur_mtype' in sourceobj.keys():
			compSET['_sources'][sourcename]['cur_mtype'] = sourceobj['cur_mtype']
		if 'line' in sourceobj.keys():
			compSET['_sources'][sourcename]['line'] = sourceobj['line']
		if 'loadErr' in sourceobj.keys():
			compSET['_sources'][sourcename]['loadErr'] = sourceobj['loadErr']


		## IF the source has no cur_path (ie- it is missing?), add cur_path from its 'line'

		if not 'cur_path' in sourceobj.keys() or sourceobj['cur_path'] is None:
			reline = compSET['_sources'][sourcename]['line']
			reline2 = re.findall("\/(\/.+)\s*$",reline)
			if reline2 is not None and len(reline2)>0:
				reline2 = reline2[0]
				if reline2 == lowest:
					compSET['_sources'][sourcename]['cur_path'] = reline2
				else:
#					compSET['_sources'][sourcename]['cur_path'] = lowest
					print "FAK1", sourcename,lowest,reline2,compSET['_sources'][sourcename]
					sys.exit(0)


#			else:
#				compSET['_sources'][sourcename]['cur_path'] = lowest
#				print "FAK2", sourcename,lowest,reline,compSET['_sources'][sourcename]
#				sys.exit(0)
		## IF the source has no cur_sha (ie- it is missing), add cur_sha from its 'line' OR mark the load err if the sha was ***ed
		if not 'cur_sha' in sourceobj.keys() or sourceobj['cur_sha'] is None:
			reline = compSET['_sources'][sourcename]['line']
			reline = re.findall(r"^(.*?),",reline)
			if reline is not None and len(reline)>0:
				reline = reline[0]
				if re.search(r'^\s*([0-9a-zA-Z]+)\s*$',reline):
					compSET['_sources'][sourcename]['cur_sha'] = reline
					compSET['_sources'][sourcename]['cur_mtype'] = re.findall(r'^\s*\w+,\s*\d+,\s*[^,]*mtype\:(\w+)\s*',compSET['_sources'][sourcename]['line'])[0]
				elif re.search(r'^\s*(\*+)\s*$',reline):
					compSET['_sources'][sourcename]['loadErr'] = True
				else:
					print "FAK3", sourcename,lowest,reline,compSET['_sources'][sourcename]
					sys.exit(0)
#			else:
#				print "FAK4", sourcename,lowest,reline,compSET['_sources'][sourcename]
#				sys.exit(0)

######################################################################################################
		compObj = compSET['_sources'][sourcename]
		stateval = 'present'

		if 'cur_path' not in compObj.keys() or compObj['cur_path'] != lowest:

			if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
				print '(((1)))', compObj.keys(), lowest, '==',compObj
				print '(((2)))', compSET['_oldmaster'].keys(), lowest,compSET['_oldmaster']
			stateval = 'missing'
		elif 'loadErr' in compObj.keys() and compObj['loadErr'] == True:
			stateval = 'error'
		elif 'cur_sha' not in compObj.keys():
			stateval = 'error'
		elif 'cur_sha' not in compSET['_oldmaster'].keys() or compSET['_oldmaster']['state'] == "missing":
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
				print '(((3)))', compSET['_oldmaster'].keys(), lowest,compSET['_oldmaster']
				print '(((4)))', compObj.keys(), lowest,compObj
			stateval = 'new'

		elif compObj['cur_bsize'] != compSET['_oldmaster']['cur_bsize']:
			stateval = 'conflict'
		elif compObj['cur_sha'] != compSET['_oldmaster']['cur_sha']:
			stateval = 'conflict'
		elif compObj['cur_mtype'] != compSET['_oldmaster']['cur_mtype']:
			stateval = 'conflict'

		if stateval == 'missing':
			# Check for folder load failures
			if 'errset' in datasets.keys() and 'folderload' in datasets['errset'].keys():
				if logsetname in datasets['errset']['folderload'].keys():
					if sourcename in datasets['errset']['folderload'][logsetname].keys():
						failedLoadList = datasets['errset']['folderload'][logsetname][sourcename]
						# check if the lowest path starts with a failed folder load from this setname and sourcename
						for path in failedLoadList:
							reline = re.findall(r"^.*?\/(\/.*)\s*$",path)
							if reline is not None and len(reline)>0:
								local_path = reline.rstrip('/')+'/'
							if lowest.startswith(local_path) and logsetname is not None:
								stateval = 'error'


		compSET['_sources'][sourcename]['state'] = stateval

def checkCompSet(lowest,matches,compSET,steplist,logsetname,datasets):
	if '_summary' not in compSET.keys():
		compSET['_summary'] = {}

	# check for conflict with new (ie- no master present)
	shacheck={}
	for setname,setobj in compSET['_sources'].iteritems():
		if setobj['state'] == 'new':
			sha = setobj['cur_sha']
			if sha not in shacheck.keys():
				shacheck[sha]=[]
			shacheck[sha].append(setname)
	if len(shacheck.keys()) > 1:
		for sha,setobj in shacheck.iteritems():
			for sourcename in setobj:
				if sourcename in compSET['_sources'].keys():
					if compSET['_sources'][sourcename]['state'] == 'new':
						compSET['_sources'][sourcename]['state'] = 'conflict'




def summarizeCompSet(lowest,matches,compSET,steplist,logsetname,datasets):
	shacheck={}
	for sourcename,setobj in compSET['_sources'].iteritems():
		sha = setobj['cur_sha']
		if sha not in shacheck.keys():
			shacheck[sha]=[]
		shacheck[sha].append(sourcename)

	masterstate = compSET['_oldmaster']['state']
	mastersha = None
	mastermtype = 'md5'
	masterbsize = None
	if 'sha' in compSET['_summary'].keys():
		mastersha = compSET['_summary']['sha']
	if 'mtype' in compSET['_summary'].keys():
		mastermtype = compSET['_summary']['mtype']
	if 'bsize' in compSET['_summary'].keys():
		masterbsize = compSET['_summary']['bsize']

	totalstates={}
	groupstates={}
	c=0
	for sourcename,setobj in compSET['_sources'].iteritems():
		c=c+1
		if setobj['state'] not in totalstates.keys():
			totalstates[  setobj['state']  ]=0
		totalstates[  setobj['state']  ]+=1
		if setobj['state'] not in groupstates.keys():
			groupstates[  setobj['state']  ]=[]
		groupstates[  setobj['state']  ].append(sourcename)
	totalstates['_total']=c


	overallstate = 'present'
	if 'error' in totalstates.keys():
		overallstate = 'error'
	elif 'conflict' in totalstates.keys():
		overallstate = 'conflict'
	elif 'missing' in totalstates.keys():
		overallstate = 'missing'
	elif 'moved' in totalstates.keys():
		overallstate = 'moved'
	elif 'new' in totalstates.keys():
		overallstate = 'new'

	compset = []
	if masterstate != "missing":
		compset.append("_oldmaster")
	for sourcename,item in compSET['_sources'].iteritems():
		if item['state'] != "missing" and item['cur_path'] == lowest:
			compset.append(sourcename)

	for sourcename in compSET['_sources'].keys():
		item = compSET['_sources'][sourcename]
		if item['state'] == 'moved_away':
			del compSET['_sources'][sourcename]


	pstate="mP"
	if masterstate == "missing":
		pstate="mX"
	missingC=0
	for sourcename,item in compSET['_sources'].iteritems():
		if item['state'] == "missing":
			missingC+=1
	if missingC == 0:
		pstate="sPdP"+pstate
	elif missingC>0 and missingC<len(compSET['_sources'].keys()):
		pstate="sPdX"+pstate
	else:
		pstate="sXdX"+pstate


	total = totalstates['_total']
	if 'missing' in totalstates.keys() and totalstates['missing'] == total:
		sstate="sX"
	elif 'error' in totalstates.keys() and totalstates['error'] == total:
		sstate="sE"
	elif mastersha is not None and mastersha in shacheck.keys():
		sstate="sS"
	elif mastersha is not None:
		sstate="sS'"
	else:
		sstate="sS"

	if 'error' in totalstates.keys():
		sstate=sstate+"dE"
	elif len(shacheck.keys()) > 1:
		sstate=sstate+"dS'"
	elif 'missing' in totalstates.keys():
		sstate=sstate+"dX"
	else:
		sstate=sstate+"dS"

	if masterstate == "missing":
		sstate=sstate+"mX"
	else:
		sstate=sstate+"mS"

	compSET['_summary']['overall']=overallstate
	compSET['_summary']['pstate']=pstate
	compSET['_summary']['sstate']=sstate
	compSET['_summary']['masterstate']=masterstate
	compSET['_summary']['mastersha']=mastersha
	compSET['_summary']['masterbsize']=masterbsize
	compSET['_summary']['mastermtype']=mastermtype
	compSET['_summary']['totalstates']=totalstates
	compSET['_summary']['groupstates']=groupstates
	compSET['_summary']['compset']=compset
	compSET['_summary']['hashes']={}
	compSET['_summary']['hashes'][mastermtype]=mastersha

def incrementPtrs(shaset,steplist,useopts):
#		inclist=[]
#		print
	for name,item in steplist.iteritems():
		steplist[name]['isnew']=False
#			print 'add: ', i,isinstance(item,dict),item
#			if isinstance(item,dict):
#				inclist.append(i)
	incrementListed(steplist,shaset,useopts)



def incrementListed(steplist,inclist,useopts):
#		print
#		print '  inclist: ',inclist
	for name in inclist:
#			print '   . ',name,steplist.keys()
		if name in steplist.keys():
			if name == "_newmaster":
				continue
#				print '   . . ',steplist[name]['pos'],steplist[name]['obj'].tell()
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
				print ' .inc:',name,'increment',steplist[name]['pos'],'=>',steplist[name]['obj'].tell()
			steplist[name]['pos']=steplist[name]['obj'].tell()
			steplist[name]['isnew']=True

def resetLogPos(logitem):
	curpos=logitem['obj'].tell()
	if curpos != logitem['pos']:
		logitem['obj'].seek( logitem['pos'] )
		return True
	return False

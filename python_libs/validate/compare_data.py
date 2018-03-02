
from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv
from sys import version_info



def sortLogByPath(logpath):
	writefile = open(logpath+'.tmp', 'w')
	readfile = csv.reader(open(logpath), delimiter=",")
	filteredRows = filter(lambda x: len(x) > 3, readfile)
	for line in sorted(filteredRows, key=lambda line: line[3]):
		strng=','.join(line)
		writefile.write(strng+'\n')
	writefile.close()

	os.remove(logpath)
	os.rename(logpath+".tmp",logpath)


def logMissedFolders(datasets,summarylog,useopts):

	if '_holddata' in useopts.keys():
		if 'dropold' in useopts['_holddata'].keys():
			print '----------- master files dropped -----------'
			driveutils.addToLog( "----------- master files dropped -----------\n", summarylog )
			for obj in useopts['_holddata']['dropold']:
				reline = obj['line']
#				reline = re.findall("^(?:[^,]+,){3}.*?(\/.*\/\/.*)$",reline)[0]

				print obj['runname'], ',', obj['logsetname'], ',', reline
				driveutils.addToLog( obj['runname']+','+obj['logsetname']+','+reline+"\n", summarylog )
			print '----------------------------------------------'
			driveutils.addToLog( "----------------------------------------------\n", summarylog )

	errfolderc=0
	if 'errset' in datasets.keys():
		if 'folderload' in datasets['errset'].keys():
			print '--------- errs: folder loads failed ---------'
			driveutils.addToLog( "--------- errs: folder loads failed ---------\n\n", summarylog )
			for logsetname,setobj in datasets['errset']['folderload'].iteritems():
				for sourcename,folderlist in datasets['errset']['folderload'].iteritems():
					for folderpath in folderlist:
						print logsetname,',', sourcename,' -  ',folderpath
						driveutils.addToLog( logsetname+', '+sourcename+' -  '+folderpath+"\n", summarylog )
						errfolderc+=1
			print '----------------------------------------------'
			driveutils.addToLog( "----------------------------------------------\n", summarylog )

	print
	if '_holddata' in useopts.keys():
		if 'dropold' in useopts['_holddata'].keys():
			print 'dropped: ',len(useopts['_holddata']['dropold'])," files from the master list"
			driveutils.addToLog( '\ndropped: '+str(len(useopts['_holddata']['dropold']))+" files from the master list\n", summarylog )
	if errfolderc>0:
			print 'errored on loading ',errfolderc," folders"
			driveutils.addToLog( '\nerrored on loading '+str(errfolderc)+" folders\n", summarylog )
	print '----------------------------------------------'
	driveutils.addToLog( "----------------------------------------------\n", summarylog )


#def actOnUseOpts(stage,useopts,masterlist,logsetname,etcdata=None):
def actOnUseOpts(stage,useopts,steplist,masterlist,runname,logsetname,compSET):
	py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

	##  If the stage is 'add', set aside any missing values from "master" into 'dropold' or 'askold' in '_holddata'
	if stage == "add":
		if 'dropold' in useopts.keys():
			if compSET['_summary']['masterstate'] != "missing":
				statelist=compSET['_summary']['groupstates'].keys()
				if len(statelist)==1 and "missing" in statelist:

					if 'dropold' not in useopts['_holddata'].keys():
						useopts['_holddata']['dropold']=[]
					useopts['_holddata']['dropold'].append({'line':compSET['_summary']['masterline'],'runname':runname,'logsetname':logsetname})
					return 'exit'
		elif 'askdropold' in useopts.keys():
			if compSET['_summary']['masterstate'] != "missing":
				statelist=compSET['_summary']['groupstates'].keys()
				if len(statelist)==1 and "missing" in statelist:
					if '_holddata' not in useopts.keys():
						useopts['_holddata']={}
					if 'askold' not in useopts['_holddata'].keys():
						useopts['_holddata']['askold']=[]
					useopts['_holddata']['askold'].append({'line':compSET['_summary']['masterline'],'runname':runname,'logsetname':logsetname})#,'set':compSET['_summary']})
					return 'exit'

	if stage == 'end':
		if 'askdropold' in useopts.keys():
			if '_holddata' in useopts.keys():
				if 'askold' in useopts['_holddata'].keys():
					heldlist=[]
					for obj in useopts['_holddata']['askold']:
						if obj['runname']==runname and obj['logsetname']==logsetname:
							heldlist.append(obj)

					if len(heldlist)==0:
						return
					print
					print
					for obj in heldlist:
						reline = obj['line']
						reline = re.findall("^(?:[^,]+,){3}.*?\/\/(.*)$",reline)[0]
						print obj['runname'], ' ', obj['logsetname'], ' ', reline
					print
					print "These files were not found."
					print "Do you wish to remove these missing files from the master list?"
					if py3:
						conf = input()
					else:
						conf = raw_input()
					print
					if re.match("^\s*([Yy](?:[Ee][Ss])?)\s*$",conf):
						print "Removed."
						if 'dropold' not in useopts['_holddata'].keys():
							useopts['_holddata']['dropold']=[]
						useopts['_holddata']['dropold'].extend(heldlist)

					else:
						newlog=masterlist['_newmaster']
						for obj in heldlist:
#							fullpath = re.findall(r'(\/\/.*)$',obj['line'])[0]
#							startline = re.findall(r'^(\w+,\s*\d+,[^,]+,\s*)\/',obj['line'])[0]
#							masterline = startline+"/masterpath/"+logsetname+fullpath+"\n"

							newlog['obj'].write(obj['line']+"\n")
						print "Canceling removal."



##################################################

def beginCompareStage(logsetlist,runname,masterlogset,masterroute,timestamp,targetlist,datasets,useopts=None):

	if useopts is None:
		useopts={}
	useopts['_holddata']={}

	debuglog = masterroute+'master-'+timestamp+'/' + 'md5vali-debug-'+datasets['timestr']+'.txt'


	newmasterlog=masterroute+'master-'+timestamp+'/'
	newmasterlog+='md5vali-master-'+timestamp+'.txt'


	##  Grab List of SetNames from datasets['logset'][runname]
	loglistkeys = logsetlist.keys()
	loglistkeys.sort()
	for logsetname in loglistkeys:
		if logsetname == "_oldmaster" or logsetname == "newmaster":
			print "**** ERROR!! ****"
			print "Do not name any filesets '_oldmaster' or '_newmaster'"
			raise
			return

		if logsetname in masterlogset.keys():
			masterlog = masterlogset[logsetname]['path']
			compareSourcesAndTargets(runname,masterlog,newmasterlog,logsetlist[logsetname],logsetname,targetlist,datasets,useopts)


	summarylog = masterroute+'md5vali-summary-'+timestamp+'.txt'
	driveutils.createNewLog(summarylog,True)

	print '----------------------------------------------'
	print
	driveutils.addToLog( "----------------------------------------------\n\n", summarylog )
	logMissedFolders(datasets,summarylog,useopts)

	os.rename(newmasterlog+".tmp",newmasterlog)
	sortLogByPath(newmasterlog)

	sumlist={}
############################### BROKE AT HERE #######################################
	for runname,runset in useopts['_holddata']['totals'].iteritems():
		if runname not in sumlist.keys():
			sumlist[runname]={}
		for logsetname,logset in useopts['_holddata']['totals'][runname].iteritems():
			for sourcename,nameset in useopts['_holddata']['totals'][runname][logsetname].iteritems():
				if sourcename not in sumlist[runname].keys():
					sumlist[runname][sourcename]={}
				for tresult,val in nameset.iteritems():
					if tresult not in sumlist[runname][sourcename].keys():
						sumlist[runname][sourcename][tresult]=0
					sumlist[runname][sourcename][tresult]+=val

	print
	print '----------------------------------------------'
	print '-----------------totals-----------------------'
	driveutils.addToLog( "\n----------------------------------------------\n", summarylog )
	driveutils.addToLog( "-----------------totals-----------------------\n", summarylog )

	for runname,runset in useopts['_holddata']['totals'].iteritems():
		for logsetname,logset in useopts['_holddata']['totals'][runname].iteritems():
			for sourcename,nameset in useopts['_holddata']['totals'][runname][logsetname].iteritems():
				strr=""
				for tresult,val in nameset.iteritems():
					strr=strr+tresult+"="+str(val)+'  '
				print ' - totals: ',runname,'-',logsetname,'-',sourcename,' : '+strr.rstrip()
				driveutils.addToLog( ' - totals:  '+runname+' - '+logsetname+' - '+sourcename+'  :  '+strr.rstrip()+"\n", summarylog )
#			useopts['_holddata']['totals'][runname][logsetname][tname][tresult]+=1
	print '----------------------------------------------'
	print '-----------------overall-----------------------'
	driveutils.addToLog( "----------------------------------------------\n", summarylog )
	driveutils.addToLog( "-----------------overall-----------------------\n", summarylog )

	for runname,runset in sumlist.iteritems():
		for sourcename,nameset in sumlist[runname].iteritems():
			strr=""
			for tresult,val in sumlist[runname][sourcename].iteritems():
				strr=strr+tresult+"="+str(val)+'  '
			print ' - sum: ',runname,'-',sourcename,' : '+strr.rstrip()
			driveutils.addToLog( ' - sum:  '+runname+' - '+sourcename+'  :  '+strr.rstrip()+"\n", summarylog )

	driveutils.addToLog( "-----------------\n", summarylog )
	print '-----------------'

	strr=""
	for tresult,val in useopts['_holddata']['overalltotals'].iteritems():
		strr=strr+tresult+': '+str(val)+',   '
	print ' - sets:   ',(strr.rstrip())[0:-1]
	strr=(strr.rstrip())[0:-1]
	driveutils.addToLog( ' - sets:    '+strr+"\n", summarylog )
	print '\n - logged in:  ',newmasterlog
#			useopts['_holddata']['overalltotals'][grouptype]=0
	useopts['_holddata']['overalltotals']={}


	if 'errset' in datasets.keys():
		print
		print '----------------------------------------------'
		driveutils.addToLog( '\n----------------------------------------------\n', summarylog )
		for typename,typelist in datasets['errset'].iteritems():
			print '------------------',typename,'-----------------------'
			driveutils.addToLog( '------------------'+typename+'-----------------------\n', summarylog )
			for item in typelist:
				print item
				driveutils.addToLog( item+'\n', summarylog )
		print '----------------------------------------------'
		driveutils.addToLog( '----------------------------------------------\n\n', summarylog )
		print


def loadStepList(steplist):
	for name,item in steplist.iteritems():
		logObj = steplist[name]['obj']

		if 'pos' in item.keys():
#				steplist[name]['pos']=logObj.tell()
			resetLogPos(steplist[name])
			aline=logObj.readline()
#				print '##',name,aline
#				if aline is None:
#					print "#!"
			steplist[name]['line']=aline

def prepStepListVals(steplist):
	for name,item in steplist.iteritems():
		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		regE1 = r'^\*+, \-?[0-9]+,'
		regE2 = r'^(?:\*|[0-9])+, \*+,'
		regE3 = r'^[A-Za-z0-9]+, -1,'

		if 'loadErr' in steplist[name].keys():
			del steplist[name]['loadErr']


		if 'line' in item.keys():
#				print 'x ',name,item.keys(),item['line'].rstrip()
			if re.search(reg,item['line']):
				l = item['line']
				Acompare = driveutils.decomposeFileLog(item['line'],1)
				steplist[name]['cur_sha']=Acompare['sha']

				groups = re.findall(r'\/(\/.*)$',Acompare['fullpath'])
				steplist[name]['cur_path']=groups[0]

				steplist[name]['line']=l
			elif re.search(regE1,item['line']) or re.search(regE2,item['line']) or re.search(regE3,item['line']):
				l = item['line']
				Acompare = driveutils.decomposeFileLog(item['line'],1)
				steplist[name]['cur_sha']=Acompare['sha']

				groups = re.findall(r'\/(\/.*)$',Acompare['fullpath'])
				steplist[name]['cur_path']=groups[0]
				steplist[name]['loadErr']=True
				steplist[name]['line']=l
			else:
#				print "########",name,item
				steplist[name]['cur_path']=None
				steplist[name]['cur_sha']=None

def comparePathsInLogSet(matches,filelist):
	for sourcename,item in filelist.iteritems():
		if 'cur_path' in item.keys():
			curpath = item['cur_path']
			print '@ ',n,item['pos'],curpath,item.keys()
			if curpath is not None:
				if curpath not in matches.keys():
					matches[curpath]=[]

				matches[curpath].append(sourcename)
	return matches

def findLowestPath(matches):
	lowest=None
	for n,item in matches.iteritems():
#			print '==',n,item
		if lowest is None:
			lowest=n
		elif lowest>n:
			lowest=n
#		print
	print 'found: ',lowest
	return lowest

def buildCompSet(lowest,matches,compSET,masterlist):
	compSET['_oldmaster']={}

	compSET['_oldmaster']['state'] = 'missing'
	compSET['_oldmaster']['cur_path'] = lowest

	if 'cur_path' in masterlist["_oldmaster"].keys():
		if lowest == masterlist["_oldmaster"]["cur_path"]:
			compSET['_oldmaster']['state'] = 'present'
			compSET['_oldmaster']['line'] = masterlist["_oldmaster"]["line"]
			compSET['_oldmaster']['cur_path'] = masterlist["_oldmaster"]["cur_path"]
			compSET['_oldmaster']['cur_sha'] = masterlist["_oldmaster"]["cur_sha"]
			compSET['_oldmaster']['cur_errs'] = []

##% _oldmaster {'obj': <open file '/drives/c/Users/kingf/logs//md5vali/dokko_backup/master/master-20170611-143943/md5vali-master-20170611-143943.txt', mode 'rb' at 0xffddaf40>, 'cur_path': '/Extensions/dhdgffkkebhmkfjojejmpbldmpobfkfo/4.2.7_0/_locales/ja/about.txt', 'logpath': '/drives/c/Users/kingf/logs//md5vali/dokko_backup/master/master-20170611-143943/md5vali-master-20170611-143943.txt', 'pos': 287186L, 'line': '41e5298bdb3b42d2cf195bc0b45debf44a90a32253a69b87a4834f5246165a46, 309, Sun Jun 11 12:58:29 2017, /masterpath/efset5//Extensions/dhdgffkkebhmkfjojejmpbldmpobfkfo/4.2.7_0/_locales/ja/about.txt\n', 'cur_sha': '41e5298bdb3b42d2cf195bc0b45debf44a90a32253a69b87a4834f5246165a46'}
def addToCompSet(lowest,matches,compSET,steplist,logsetname,datasets):
	compSET['_summary'] = {}
	compSET['_summary']['path'] = lowest
	if 'cur_sha' in compSET['_oldmaster'].keys():
		compSET['_summary']['sha'] = compSET['_oldmaster']['cur_sha']

	compSET['_sources']={}
	for sourcename,sourceobj in steplist.iteritems():
		compSET['_sources'][sourcename] = {}

		if 'cur_path' in sourceobj.keys():
			compSET['_sources'][sourcename]['cur_path'] = sourceobj['cur_path']
		if 'cur_sha' in sourceobj.keys():
			compSET['_sources'][sourcename]['cur_sha'] = sourceobj['cur_sha']
		if 'line' in sourceobj.keys():
			compSET['_sources'][sourcename]['line'] = sourceobj['line']
		if 'loadErr' in sourceobj.keys():
			compSET['_sources'][sourcename]['loadErr'] = sourceobj['loadErr']

		## IF the source has no cur_path (ie- it is missing?), add cur_path from its 'line'
		if not 'cur_path' in sourceobj.keys():
			reline = compSET['_sources'][sourcename]['line']
			reline = re.findall("^\/(\/.*)\s*$",reline)
			if reline is not None and len(reline)>0:
				reline = reline[0]
				if reline == lowest:
					compSET['_sources'][sourcename]['cur_path'] = reline
		## IF the source has no cur_sha (ie- it is missing), add cur_sha from its 'line' OR mark the load err if the sha was ***ed
		if not 'cur_sha' in sourceobj.keys():
			reline = compSET['_sources'][sourcename]['line']
			reline = re.findall("^(.*?),",reline)
			if reline is not None and len(reline)>0:
				reline = reline[0]
				if re.search(r'^\s*([0-9a-zA-Z]+)\s*$',reline):
					compSET['_sources'][sourcename]['cur_sha'] = reline
				elif re.search(r'^\s*(\*+)\s*$',reline):
					compSET['_sources'][sourcename]['loadErr'] = True
######################################################################################################
		compObj = compSET['_sources'][sourcename]
		stateval = 'present'

		if 'cur_path' not in compObj.keys() or compObj['cur_path'] != lowest:
			stateval = 'missing'
		elif 'loadErr' in compObj.keys() and compObj['loadErr'] == True:
			stateval = 'error'
		elif 'cur_sha' not in compObj.keys():
			stateval = 'error'
		elif 'cur_sha' not in compSET['_oldmaster'].keys() or compSET['_oldmaster']['state'] == "missing":
			stateval = 'new'
		elif compObj['cur_sha'] != compSET['_oldmaster']['cur_sha']:
			stateval = 'conflict'

		if stateval == 'missing':
			# Check for folder load failures
			if 'errset' in datasets.keys() and 'folderload' in datasets['errset'].keys():
				if logsetname in datasets['errset']['folderload'].keys():
					if sourcename in datasets['errset']['folderload'][logsetname].keys():
						failedLoadList = datasets['errset']['folderload'][logsetname][sourcename]
						# check if the lowest path starts with a failed folder load from this setname and sourcename
						for path in failedLoadList:
							reline = re.findall("^.*?\/(\/.*)\s*$",path)
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
	if 'sha' in compSET['_summary'].keys():
		mastersha = compSET['_summary']['sha']

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
	elif 'new' in totalstates.keys():
		overallstate = 'new'

	compset = []
	if masterstate != "missing":
		compset.append("_oldmaster")
	for sourcename,item in compSET['_sources'].iteritems():
		if item['state'] != "missing" and item['cur_path'] == lowest:
			compset.append(sourcename)


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
	compSET['_summary']['totalstates']=totalstates
	compSET['_summary']['groupstates']=groupstates
	compSET['_summary']['compset']=compset

def incrementPtrs(shaset,steplist):
#		inclist=[]
#		print
#		for i,item in shaset.iteritems():
#			print 'add: ', i,isinstance(item,dict),item
#			if isinstance(item,dict):
#				inclist.append(i)
	incrementListed(steplist,shaset)

def closeUpFiles(filelist):
	for i,item in filelist.iteritems():
		if 'obj' in item.keys():
			item['obj'].close()
#				print 'closed: ',i

def	writeOutput(compSET,newlog,runname,logsetname,steplist,masterlist,datasets,useopts=None):
	if useopts is None:
		useopts={}
	if '_holddata' not in useopts.keys():
		useopts['_holddata']={}
##		print compset.keys(),newlog.keys()
##		print compset
##		print
##		print compset

	masterfilepath = "/masterpath/"+logsetname+"/"+compSET['_summary']['path']
	masterfiledata = None
	masterline = None
	if compSET['_summary']['masterstate'] != 'missing':
		if 'line' in compSET['_oldmaster'].keys():
			relook=re.findall(r'^(\w+,\s*\d+,[^,]+,\s*)\/',compSET['_oldmaster']['line'])
			if len(relook)>0:
				masterfiledata = relook[0]
	if masterfiledata is None:
		statelist = compSET['_summary']['groupstates'].keys()
		arrs=[]
		if 'new' in statelist:
			arrs.extend(  compSET['_summary']['groupstates']['new']  )
		if 'present' in statelist:
			arrs.extend(  compSET['_summary']['groupstates']['present']  )
		if len(arrs) > 0:
			c=0
			while masterfiledata is None or c<len(arrs):
				sourcename=arrs[c]
				if sourcename in compSET['_sources'].keys():
					if 'line' in compSET['_sources'][sourcename].keys():
						relook=re.findall(r'^(\w+,\s*\d+,[^,]+,\s*)\/',compSET['_sources'][sourcename]['line'])
						if len(relook)>0:
							masterfiledata = relook[0]
				c+=1
	if masterfiledata is not None:
		masterline = masterfiledata+masterfilepath+"\n"
		compSET['_summary']['masterline']=masterline.rstrip()

#		val = actOnUseOpts('add',useopts,masterlist,logsetname,{'logitem':logitem,'compset':compset})
	val = actOnUseOpts('add',useopts,steplist,masterlist,runname,logsetname,compSET)
	if val == 'exit':
		return

	if masterline is not None:
		print "==== ",masterline
		newlog['obj'].write(masterline)



	addToTotalCount(useopts['_holddata'],runname,logsetname,compSET)

	overall=compSET['_summary']['overall']
	logpath=masterlist['_newmaster']['newpath']+'/md5vali-'+overall+'-'+masterlist['_newmaster']['newtime']+'.txt'
	driveutils.createNewLog(logpath,True)

	driveutils.addToLog( "\n-------- md5 "+overall+" --------\n", logpath )
	print
	print "-------- md5 "+overall+" --------"
	if compSET['_summary']['masterstate'] == "missing" or masterline is None:
		print "master - missing, "+masterfilepath
		driveutils.addToLog( "master - missing, "+masterfilepath+"\n", logpath )
	else:
		print "master - "+masterline.rstrip()
		driveutils.addToLog( "master - "+masterline, logpath )

##################################***************************############## value in sourceobj['line'] is wrong!
	for sourcename,sourceobj in compSET['_sources'].iteritems():
		if sourceobj['state'] == 'missing':
			if compSET['_summary']['masterstate'] != "missing" and masterline is not None:
				groups1 = re.findall(r'^(\w+,\s*\d+,\s*[^,]+,\s*)\/masterpath\/.*?\/\/.*?\s*$',masterline.rstrip())
				groups2 = re.findall(r'^\w+,\s*\d+,\s*[^,]+,\s*\/masterpath\/.*?\/\/(.*?)\s*$',masterline.rstrip())
				templinebody=groups1[0]
				masterrelativepath=groups2[0]
				temppath=None
				for logitem in datasets['loglist']:
					print
					if 'setname' in logitem.keys() and 'sourcename' in logitem.keys() and 'path' in logitem.keys():
						print logitem['setname'],'==',logsetname,'and',logitem['sourcename'],'==',sourcename
						if logitem['setname'] == logsetname and logitem['sourcename'] == sourcename:
							temppath = logitem['path']+'/'+masterrelativepath
				if temppath is not None:
					templinebody+=temppath
					print sourcename,"- missing, "+templinebody.rstrip()
					driveutils.addToLog( sourcename+"- missing, "+templinebody+"\n", logpath )
				else:
					print sourcename,"- missing, "+masterrelativepath.rstrip()
					sys.exit(1)
			else:
				######################## find a line from a partner object elsewhere?
				print sourcename,"- missing, "+sourceobj['line'].rstrip()
				driveutils.addToLog( sourcename+"- missing, "+sourceobj['line'], logpath )
		else:
			highlight = sourceobj['state']
			if highlight == 'present':
				highlight = 'match'

			print sourcename,"- "+highlight+", "+sourceobj['line'].rstrip()
			driveutils.addToLog( sourcename+"- "+highlight+", "+sourceobj['line'], logpath )

	print "* ",compSET["_summary"]['pstate'],compSET["_summary"]['sstate']
	driveutils.addToLog( "* "+compSET["_summary"]['pstate']+" "+compSET["_summary"]['sstate'], logpath )

	matchnames=[]
	for sourcename,sourceobj in compSET['_sources'].iteritems():
		if 'state' in sourceobj.keys():
			if sourceobj['state'] == 'new' or sourceobj['state'] == 'present':
				matchnames.append(sourcename)
	if compSET['_summary']['masterstate'] != "missing":
		matchnames.append("_oldmaster")

	return matchnames


def addToTotalCount(optcount,runname,logsetname,compSET):
	if 'overalltotals' not in optcount.keys():
		optcount['overalltotals']={}

	if 'totals' not in optcount.keys():
		optcount['totals']={}
	if runname not in optcount['totals'].keys():
		optcount['totals'][runname]={}
	if logsetname not in optcount['totals'][runname].keys():
		optcount['totals'][runname][logsetname]={}
	for sourcename,sourceobj in compSET['_sources'].iteritems():
		if sourcename not in optcount['totals'][runname][logsetname].keys():
			optcount['totals'][runname][logsetname][sourcename]={}
		state = sourceobj['state']
		if state not in optcount['totals'][runname][logsetname][sourcename].keys():
			optcount['totals'][runname][logsetname][sourcename][state]=0

		optcount['totals'][runname][logsetname][sourcename][state]+=1

	overall=compSET['_summary']['overall']
	if overall not in optcount['overalltotals'].keys():
		optcount['overalltotals'][overall]=0
	optcount['overalltotals'][overall]+=1






def stepCompareLogs(c,steplist,masterlist,runname,logsetname,datasets,useopts=None):
	if useopts is None:
		useopts={}

	loadStepList(steplist)
	prepStepListVals(steplist)

	loadStepList(masterlist)
	prepStepListVals(masterlist)

	# DEFUNCT?
	pushMasterListToGroup(masterlist,logsetname)


	matches = {}
	comparePathsInLogSet(matches,steplist)
	comparePathsInLogSet(matches,masterlist)

#		print
	for i,item in matches.iteritems():
		print ':',i,item

	lowest = findLowestPath(matches)
	if lowest is None:
		print '----------------------------------------------'
		print '----------------------------------------------'
		return {'count':None,'lowest':None}

	compSET = {}
	buildCompSet(lowest,matches,compSET,masterlist)
	addToCompSet(lowest,matches,compSET,steplist,logsetname,datasets)
	checkCompSet(lowest,matches,compSET,steplist,logsetname,datasets)
	for i,item in compSET["_sources"].iteritems():
		print '%',i,item['state'],item['cur_sha'],item['cur_path']
	summarizeCompSet(lowest,matches,compSET,steplist,logsetname,datasets)
	for i,item in compSET["_summary"].iteritems():
		print '>',i,item



	matchnames = writeOutput(compSET,masterlist['_newmaster'],runname,logsetname,steplist,masterlist,datasets,useopts)
	outputxt = '# '+str(c)+' ! '+lowest+' ! '+compSET["_summary"]['pstate']+', '+compSET["_summary"]['sstate']+', '+str(matchnames)
	print outputxt

	incrementPtrs(compSET['_summary']['compset'],steplist)
	incrementPtrs(compSET['_summary']['compset'],masterlist)

	print '----------------------------------------------'
	print '----------------------------------------------'
	return {'count':c+1,'lowest':lowest}


def resetLogPos(logitem):
	curpos=logitem['obj'].tell()
	if curpos != logitem['pos']:
		logitem['obj'].seek( logitem['pos'] )

def pushMasterListToGroup(masterlist,logsetname):
	for name,item in masterlist.iteritems():
		logObj = masterlist[name]['obj']
#			print 't  ',name,item

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if 'line' in item.keys():
			print 'y  ',item['line']
			while re.search(reg,item['line']):
#				if re.search(reg,item['line']):
				l = item['line']
#					print 'XXX',name,item['line'],masterlist.keys()

				Acompare = driveutils.decomposeFileLog(item['line'],1)
				masterlist[name]['line']=l

				groups = re.findall(r'\/masterpath\/(.*?)\/\/.*$',Acompare['fullpath'])
				groupname=groups[0]


				if groupname != logsetname:
					print '     .  . skip: ',groupname,'!=',logsetname,': ',Acompare['fullpath'].rstrip()
#						print 'skip: ',groupname, logsetname, name
					incrementListed(masterlist,[name])
					loadStepList(masterlist)
					prepStepListVals(masterlist)
				else:
#						print 'up: ',groupname, logsetname, masterlist.keys()
					loadStepList(masterlist)
					prepStepListVals(masterlist)
					break

def incrementListed(steplist,inclist):
#		print
#		print '  inclist: ',inclist
	for name in inclist:
#			print '   . ',name,steplist.keys()
		if name in steplist.keys():
#				print '   . . ',steplist[name]['pos'],steplist[name]['obj'].tell()
			steplist[name]['pos']=steplist[name]['obj'].tell()


def compareSourcesAndTargets(runname,masterlog,newmasterlog,logset,logsetname,targetlist,datasets,useopts=None):
	if useopts is None:
		useopts={}

	steplist={}
#	i=0
	for sourcename,logpath in logset.iteritems():
		logAf = open(logpath, 'rb')
		steplist[sourcename]={}
		steplist[sourcename]['obj']=logAf
		steplist[sourcename]['pos']=0
		steplist[sourcename]['logpath']=logpath
#		steplist[sourcename]['sourcename']=sourcename

	masterlist={}

	masterlist['_oldmaster']={}
	logBf = open(masterlog, 'rb')
	masterlist['_oldmaster']['obj']=logBf
	masterlist['_oldmaster']['pos']=0
	masterlist['_oldmaster']['logpath']=masterlog

	masterlist['_newmaster']={}
	driveutils.createNewLog(newmasterlog+'.tmp',True)
	logBf = open(newmasterlog+'.tmp', 'ab')
	masterlist['_newmaster']['obj']=logBf
	masterlist['_newmaster']['logpath']=newmasterlog

	masterlist['_newmaster']['newpath']=re.findall('^(.*)\/',newmasterlog)[0]
	masterlist['_newmaster']['newtime']=re.findall('^.*-(\d+-\d+)\/',newmasterlog)[0]


	print
	c=0
	opath=''
#	print masterlist['_oldmaster']
	while True:
		col=stepCompareLogs(c,steplist,masterlist,runname,logsetname,datasets,useopts)
#		print '| check: ',c,opath,col['lowest']
#		print '----------------------------------------------'
		if(opath == col['lowest'] and c>0):
			break
		if(col['lowest'] is None and col['count'] is None):
			break
		c=col['count']
		opath=col['lowest']

	actOnUseOpts('end',useopts,steplist,masterlist,runname,logsetname,{})

	closeUpFiles(steplist)
	closeUpFiles(masterlist)
#	return
#	os.rename(newmasterlog+".tmp",newmasterlog)
	sortLogByPath(newmasterlog+".tmp")

from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import datetime
from sys import version_info

def	writeOutput(compSET,newlog,runname,logsetname,steplist,masterlist,datasets,useopts=None):
	if useopts is None:
		useopts={}
	if '_holddata' not in useopts.keys():
		useopts['_holddata']={}

	# if master data is present, harvest file information (md5, filesize, date) for use
	################# EXTRA / stuff here?
	masterfilepath = "/masterpath/"+logsetname.rstrip('/')+'//'+compSET['_summary']['path'].lstrip('/')
	masterfiledata = None
	masterline = None
	if compSET['_summary']['masterstate'] != 'missing':
		if 'line' in compSET['_oldmaster'].keys():
			relook=re.findall(r'^(\w+,\s*\d+,\s*\w[^,]*,\s*)\/',compSET['_oldmaster']['line'])
			if len(relook)>0:
				masterfiledata = relook[0]
	if masterfiledata is None:
		statelist = compSET['_summary']['groupstates'].keys()
		arrs=[]
		if 'new' in statelist:
			arrs.extend(  compSET['_summary']['groupstates']['new']  )
		if 'present' in statelist:
			arrs.extend(  compSET['_summary']['groupstates']['present']  )
		if 'moved' in statelist:
			arrs.extend(  compSET['_summary']['groupstates']['moved']  )
		if len(arrs) > 0:
			c=0
			while masterfiledata is None or c<len(arrs):
				sourcename=arrs[c]
				if sourcename in compSET['_sources'].keys():
					if 'line' in compSET['_sources'][sourcename].keys():
						relook=re.findall(r'^(\w+,\s*\d+,\s*\w[^,]*,\s*)\/',compSET['_sources'][sourcename]['line'])
						if len(relook)>0:
							masterfiledata = relook[0]
				c+=1
	if masterfiledata is not None:
		if logsetname in datasets['targets'].keys() and 'source' in datasets['targets'][logsetname].keys():
			grouppath=datasets['targets'][logsetname]['source']
		if 'source' in datasets['found'].keys():
			drivepath=datasets['found']['source']
		if grouppath is not None and drivepath is not None:
			basepath=drivepath.rstrip('/')+"/"+grouppath.rstrip('/')+"/"

		basepath=comparefns.grabBasePath(logsetname,'source',datasets)
		masterend='/masterpath/'+logsetname+'/'+compSET['_summary']['path']
		print ' GETx ','newmaster',compSET['_summary']
		newermasterline=comparefns.redoDataFile(masterfiledata+masterend,logsetname,compSET['_summary']['path'],basepath,compSET['_summary']['hashes'],useopts)
		print '  - after redoX:',compSET['_summary']['hashes'].keys()
		compSET['_summary']['masterline']=newermasterline.rstrip()
		masterline=newermasterline

	# IF ENTRY IS IN OLD MASTER BUT IS NOW GONE FROM ALL SOURCES, ADD TO A 'MISSING' QUICK LIST
	if compSET['_summary']['masterstate'] != "missing" and masterline is not None:
		allmissing=True
		for sourcename,sourceobj in compSET['_sources'].iteritems():
			if sourceobj['state'] != 'missing':
				allmissing=False
				break
		if allmissing:
			missinglogpath=masterlist['_newmaster']['newpath']+'/quicklists/missing-list-'+masterlist['_newmaster']['newtime']+'.txt'
			driveutils.createNewLog(missinglogpath,True)
			driveutils.addToLog(masterline, missinglogpath)


	val = dropmissed.actOnUseOpts('add',datasets,useopts,steplist,masterlist,runname,logsetname,compSET)
	if val == 'exit':
		return

	if masterline is not None:

		## Rewrite master if moved
		allmoved=True
		moveconf=False
		movepath=None
		for sourcename,sourceobj in compSET['_sources'].iteritems():
			if sourceobj['state'] != 'moved':
				allmoved=False
			elif movepath == None:
				movepath = sourceobj['moved_to']
			elif movepath != sourceobj['moved_to']:
				moveconf = True
		if allmoved and not moveconf and movepath is not None:
			oldmasterline = masterline
			newmasterstart=re.findall('^([^\/]+\/.*?\/)\/',masterline)[0]
			masterline = newmasterstart+movepath+"\n"


		mtest = None
		try:
			mtest = masterline.encode('utf-8')
		except UnicodeDecodeError as exception:
			mtest = masterline
		if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
			print "==== ",mtest
		newlog['obj'].write(mtest)


		if allmoved and not moveconf and movepath is not None and oldmasterline is not None:
			masterline = oldmasterline



	addToTotalCount(useopts['_holddata'],runname,logsetname,compSET)

##################################### WRITE OVERALL LOGS - MASTER LINE ########################
	overall=compSET['_summary']['overall']
	if overall != "present":
		logpath=masterlist['_newmaster']['newpath']+'/md5vali-'+overall+'-'+masterlist['_newmaster']['newtime']+'.txt'
		driveutils.createNewLog(logpath,True)

		driveutils.addToLog( "\n-------- md5 "+overall+" --------\n", logpath )

		if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
			print
			print "-------- md5 "+overall+" --------"

		if compSET['_summary']['masterstate'] == "missing" or masterline is None:
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
				print "master - missing, "+masterfilepath
			driveutils.addToLog( "master - missing, "+masterfilepath+"\n", logpath )
		else:
			if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
				print "master - "+masterline.rstrip()
			driveutils.addToLog( "master - "+masterline, logpath )

##################################### WRITE OVERALL LOGS - SOURCES ########################
##################################***************************############## value in sourceobj['line'] is wrong!
		for sourcename,sourceobj in compSET['_sources'].iteritems():
			if sourceobj['state'] == 'missing':
				if compSET['_summary']['masterstate'] != "missing" and masterline is not None:
					groups1 = re.findall(r'^(\w+,\s*\d+,\s*\w[^,]*,\s*)\/masterpath\/.*?\/\/.*?\s*$',masterline.rstrip())
					groups2 = re.findall(r'^\w+,\s*\d+,\s*\w[^,]*,\s*\/masterpath\/.*?\/\/(.*?)\s*$',masterline.rstrip())
					templinebody=groups1[0]
					masterrelativepath=groups2[0]
					temppath=None
					for logitem in datasets['loglist']:
						if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
							print
						if 'setname' in logitem.keys() and 'sourcename' in logitem.keys() and 'path' in logitem.keys():
							if logitem['setname'] == logsetname and logitem['sourcename'] == sourcename:
								temppath = logitem['path'].rstrip('/')+'//'+masterrelativepath.lstrip('/')
					if temppath is not None:
						templinebody+=temppath
						if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
							print sourcename,"- missing, "+templinebody.rstrip()
						driveutils.addToLog( sourcename+"- missing, "+templinebody+"\n", logpath )
					else:
						if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
							print sourcename,"- missing, "+masterrelativepath.rstrip()
						sys.exit(1)
				else:
					######################## find a line from a partner object elsewhere?
					if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
						print sourcename,"- missing, "+sourceobj['line'].rstrip()
					driveutils.addToLog( sourcename+"- missing, "+sourceobj['line'], logpath )
			elif sourceobj['state'] == 'moved':
				if re.match('^([^\/]+\/.*?\/)\/.*',sourceobj['line']):
					newsourcestart=re.findall('^([^\/]+\/.*?\/)\/',sourceobj['line'])[0]
				else:
					newsourcestart=comparefns.grabBasePath(logsetname,sourcename,datasets)
				newsourcestart=newsourcestart.rstrip('/')+'/'

				movedlogpath=masterlist['_newmaster']['newpath']+'/quicklists/moved-list-'+masterlist['_newmaster']['newtime']+'.txt'
				driveutils.createNewLog(movedlogpath,True)

				outstring = sourcename+" - moved_fr, "+newsourcestart+sourceobj['moved_from']
				mtest = None
				try:
					ostrtest = outstring.encode('utf-8')
				except UnicodeDecodeError as exception:
					ostrtest = outstring

				if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
					print ostrtest
				driveutils.addToLog( ostrtest+"\n", logpath )
				driveutils.addToLog( ostrtest+"\n", movedlogpath)

				outstring = sourcename+" - moved_to, "+newsourcestart+sourceobj['moved_to']
				mtest = None
				try:
					ostrtest = outstring.encode('utf-8')
				except UnicodeDecodeError as exception:
					ostrtest = outstring

				if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
					print ostrtest
				driveutils.addToLog( ostrtest+"\n", logpath )
				driveutils.addToLog( ostrtest+"\n", movedlogpath)
				driveutils.addToLog( "------\n", movedlogpath)
			else:
				highlight = sourceobj['state']
				if highlight == 'present':
					highlight = 'match'

				if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
					print sourcename,"- "+highlight+", "+sourceobj['line'].rstrip()
				driveutils.addToLog( sourcename+"- "+highlight+", "+sourceobj['line'], logpath )

		if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
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






def stepCompareLogs(c,steplist,masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts=None):
	if useopts is None:
		useopts={}

	comparefns.loadStepList(steplist,useopts)
	comparefns.prepStepListVals(steplist,readname,runname,logsetname,tmpfolder,datasets,useopts)

	comparefns.loadStepList(masterlist,useopts)
	comparefns.prepStepListVals(masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)

	# DEFUNCT?
	comparefns.pushMasterListToGroup(masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)


	matches = {}
	comparefns.comparePathsInLogSet(matches,steplist,useopts)
	comparefns.comparePathsInLogSet(matches,masterlist,useopts)

#		print
	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		for i,item in matches.iteritems():
			print ':',i,item

	lowest = comparefns.findLowestPath(matches,useopts)
	if lowest is None:
		if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
			print '----------------------------------------------'
		print '----------------------------------------------'
		return {'count':None,'lowest':None}

	compSET = {}
	comparefns.buildCompSet(lowest,matches,compSET,masterlist,useopts)
	comparefns.addToCompSet(lowest,matches,compSET,steplist,logsetname,datasets,useopts)
	comparefns.checkCompSet(lowest,matches,compSET,steplist,logsetname,datasets)
	if 'skipmovecheck' not in useopts.keys() or not useopts['skipmovecheck']:
		comparesearch.searchForMove(readname,runname,logsetname,tmpfolder,compSET,masterlist,datasets,useopts)


	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		for i,item in compSET["_sources"].iteritems():
			print '%',i,item['state'],item['cur_sha'],item['cur_mtype'],item['cur_path']

	comparefns.summarizeCompSet(lowest,matches,compSET,steplist,logsetname,datasets)

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		for i,item in compSET["_summary"].iteritems():
			print '>',i,item


	if len(compSET['_sources'].keys()) > 0:

		matchnames = writeOutput(compSET,masterlist['_newmaster'],runname,logsetname,steplist,masterlist,datasets,useopts)

		outputxt = '# '+str(c)+' ! '+logsetname+', '+lowest+' ! '+compSET["_summary"]['pstate']+', '+compSET["_summary"]['sstate']+', '+str(matchnames)
		print outputxt


	comparefns.incrementPtrs(compSET['_summary']['compset'],steplist,useopts)
	comparefns.incrementPtrs(compSET['_summary']['compset'],masterlist,useopts)

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		print '----------------------------------------------'
		print '----------------------------------------------'
	return {'count':c+1,'lowest':lowest}


def compareSourcesAndTargets(runname,readname,timeset,masterlog,newmasterlog,timestamp,logset,logsetname,targetlist,tmpfolder,datasets,useopts=None):
	if useopts is None:
		useopts={}

	useopts['compmode']="compare"
	useopts['timestamp']=timestamp

	if 'skipmovecheck' not in useopts.keys() or not useopts['skipmovecheck']:
		useopts['compmode']="movesearch"
		timeset['compare']['_parts']['_search'][logsetname] = {}
		timeset['compare']['_parts']['_search'][logsetname]['start'] = datetime.datetime.now()
		comparesearch.searchSourcesAndTargets(readname,runname,masterlog,newmasterlog,timestamp,logset,logsetname,targetlist,tmpfolder,datasets,useopts)

		timeset['compare']['_parts']['_search'][logsetname]['end'] = datetime.datetime.now()
		######## REMOVE ABOVE LINE
		useopts['compmode']="movebuild"
		comparesearch.buildMoveLog(readname,runname,timestamp,logset,logsetname,tmpfolder,datasets,useopts)
		timeset['compare']['_parts']['_search'][logsetname]['end'] = datetime.datetime.now()

	useopts['compmode']="compare"
	if logsetname not in timeset['compare']['_parts']['_compare'].keys():
		timeset['compare']['_parts']['_compare'][logsetname] = {}

	timeset['compare']['_parts']['_compare'][logsetname]['start'] = datetime.datetime.now()
	steplist={}

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
	masterlist['_newmaster']['newtime']=timestamp


	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		print
	c=0
	opath=''
#	print masterlist['_oldmaster']
	useopts['firstrun']=True
	while True:
		col=stepCompareLogs(c,steplist,masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)
		useopts['firstrun']=False
#		print '| check: ',c,opath,col['lowest']
#		print '----------------------------------------------'
		if(opath == col['lowest'] and c>0):
			break
		if(col['lowest'] is None and col['count'] is None):
			break
		c=col['count']
		opath=col['lowest']

	dropmissed.actOnUseOpts('end',datasets,useopts,steplist,masterlist,runname,logsetname,{})

	comparefns.closeUpFiles(steplist)
	comparefns.closeUpFiles(masterlist)
	timeset['compare']['_parts']['_compare'][logsetname]['end'] = datetime.datetime.now()
#	return
#	os.rename(newmasterlog+".tmp",newmasterlog)

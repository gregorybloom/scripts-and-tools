from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv, datetime



### DEFUNCT
def concatLogGroups(logparts):
	newloglist=[]
	for loggroup,grouplogs in logparts.iteritems():
		if 'partlog' in grouplogs.keys():
			if 'logs' in grouplogs.keys():
				newlogname = grouplogs['partlog']

				driveutils.createNewLog(newlogname,False)

				newlog = open(newlogname, 'ab')

				loglist = grouplogs['logs']
				for logitem in loglist:
					flogobj = open(logitem, 'r')
					for line in flogobj:
						newlog.write(line)
					flogobj.close()
				newlog.close()

				driveutils.sortLogByPath(newlogname)
				newloglist.append(newlogname)
	return newloglist



def grabAMasterLog(masterpath,timestamp,compopts):
	masterlog = getBestMaster(masterpath, compopts)
	if masterlog == None:
		vals = timestamp.split('-')
		val1 = int(vals[0])
		val2 = int(vals[1])-1
		while( len(str(val2)) < 6 ):
			# adds 0's to clock time denomination as necessary
			val2="0"+str(val2)

#			masterlog = 'md5vali-master-'+str(val1)+'-'+str(val2)+'.txt'
		masterlog = 'master-'+str(val1)+'-'+str(val2)+'/'
		masterlog += 'md5vali-master-'+str(val1)+'-'+str(val2)+'.txt'
		driveutils.createNewLog(masterpath+masterlog,False)
	masterlog=masterpath+masterlog
	return masterlog

def getBestMaster(masterpath,compopts):
	def checkMasterName(val1,val2,masterpath):
		val1i=val1
		val2i=val2
		mastername = buildMasterName(val1i,val2i)
		mpath = masterpath+mastername
		if os.path.exists(mpath):
			return True
		return False

	def buildMasterName(val1,val2):
		while( len(str(val1)) < 8 ):
			# adds 0's to clock time denomination as necessary
			val1="0"+str(val1)
		while( len(str(val2)) < 6 ):
			# adds 0's to clock time denomination as necessary
			val2="0"+str(val2)
		bestfit=str(val1)+'-'+str(val2)
		bestmaster = 'master-'+bestfit+'/'
		bestmaster += 'md5vali-master-'+bestfit+'.txt'
		return bestmaster

	if not os.path.exists(masterpath):
		try:
			os.makedirs(masterpath)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

	highmaster = None
	try:
		masterlist = driveutils.readDir(masterpath)
	except OSError as exception:
		raise
	if len(masterlist) == 0:
		return None
	masterlist.sort()

	bestfit1=0
	bestfit2=0
	for mastern in masterlist:
		namestr = str(mastern)
		if re.match('^master-\d+-\d+\s*$',namestr):
			groups = re.findall(r'^master-(\d+-\d+)\s*$',namestr)
			vals = groups[0].split('-')
			val = int(vals[0])

			summaryname = 'md5vali-summary-'+str(groups[0])+'.txt'
			if not summaryname in masterlist:
				continue

			if(val > bestfit1):
				if(checkMasterName(val,int(vals[1]),masterpath)==True):
					bestfit1=val
					bestfit2=int(vals[1])
			elif(val == bestfit1):
				if(bestfit2 < int(vals[1])):
					if(checkMasterName(val,int(vals[1]),masterpath)==True):
						bestfit1=val
						bestfit2=int(vals[1])

	if(bestfit1 > 0) and (bestfit2 > 0):
		bestmaster = buildMasterName(bestfit1,bestfit2)
		return bestmaster

def createNewTmpMD5Logs(runname,timestr,infosets,foundlist,logfolder,tmpfolder,timeset,runopts=None):
	if runopts is None:
		runopts={}
	if 'walkopts' not in runopts.keys():
		runopts['walkopts']={}

	logset={}
	mastset={}
	errset={}
	loglist=[]

	if runname not in logset.keys():
		logset[runname]={}
	readname=runopts['compopts']['readname']
	logpath = logfolder+'/md5vali/'+readname+'/'+runname+'/';
	tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestr+'/';

	timeset['md5walk']['_parts'] = {}

	if 'usenew_md5log' in runopts['walkopts'].keys():

		uselog=runopts['walkopts']['usenew_md5log']['logpath']
		if os.path.exists(uselog) and os.path.isfile(uselog):
			print "Using ",uselog
			driveutils.sortLogByPath(uselog)

			if 'foldersets' in infosets.keys():
				for setname,folderset in infosets['foldersets'].iteritems():
					for sourcename,folderpath in folderset.iteritems():

						if sourcename != runopts['walkopts']['usenew_md5log']['setsource']:
							continue
						if sourcename not in foundlist.keys():
							continue

						if setname not in logset[runname].keys():
							logset[runname][setname]={}

						startpath=foundlist[sourcename]
						targetpath=startpath+folderpath
						targetpath = targetpath.replace('//','/')
						targetpath = targetpath.rstrip('/')
						targetpath = targetpath+'/'


						logname= tmppath+'pieces/'+sourcename+'/'+setname+'/md5vali-'+sourcename+'-'+timestr+'.txt'
						driveutils.createNewLog(logname,True)

						filelog = open(logname, "a")
						with open(uselog) as f:
						    for rline in f.readlines():
								fpath = None
								groupsA = re.findall(r'^(?:[^,]+,){3}\s*(\/.*?\/\/.*\S)\s*$',rline)
								groupsB = re.findall(r'^((?:[^,]+,){3})\s*\/.*?\/\/.*\S\s*$',rline)
								fpath = groupsA[0]
								fdeets = groupsB[0]

								if re.match(r'^\/masterpath\/',fpath):
									groups1 = re.findall(r'^\/masterpath\/(.*?)\/\/.*$',fpath)
									groups2 = re.findall(r'^\/masterpath\/.*?\/\/(.*)$',fpath)
									testgroupname=groups1[0]
									testrelativepath=groups2[0]
									if setname != testgroupname:
										continue
									testfullpath = targetpath+'/'+testrelativepath
								else:
									groups = re.findall(r'^(\/.*?)\/\/.*$',fpath)
									testgrouppath=groups[0]
									testgrouppath = testgrouppath.rstrip('/')
									testgrouppath = testgrouppath+'/'
									if testgrouppath != targetpath:
										continue
									testfullpath = fpath

								filelog.write(fdeets+testfullpath+'\n')

						filelog.close()
						f.close()


						driveutils.sortLogByPath(logname)
						loglist.append({'log':logname,'path':targetpath,'setname':setname,'sourcename':sourcename})
						logset[runname][setname][sourcename]=logname
						masterpath=logpath+'master/';	#	md5vali-master-
						mastset[runname]=masterpath


	elif 'foldersets' in infosets.keys():
		for setname,folderset in infosets['foldersets'].iteritems():
			for sourcename,folderpath in folderset.iteritems():
				if setname not in logset[runname].keys():
					logset[runname][setname]={}

				if sourcename not in foundlist.keys():
					continue
				startpath=foundlist[sourcename]

				logname= tmppath+'pieces/'+sourcename+'/'+setname+'/md5vali-'+sourcename+'-'+timestr+'.txt'

				driveutils.createNewLog(logname,False)
				targetpath = startpath+folderpath
				targetpath = targetpath.replace('//','/')
				targetpath = targetpath.rstrip('/')
				targetpath = targetpath+'/'
				###### str replace // to /.  rstrip /. add /? (test each way)

				method=['fast']
				if 'method' in runopts['walkopts'].keys():
					method=[]
					if 'slow' in runopts['walkopts']['method'].keys():
						if setname in runopts['walkopts']['method']['slow']:
							method.append['slow']
					if 'fast' in runopts['walkopts']['method'].keys():
						if setname in runopts['walkopts']['method']['fast']:
							method.append['fast']
				if len(method) == 0:
					method=['fast']

				timeset['md5walk']['_parts'][setname]={}
				timeset['md5walk']['_parts'][setname][sourcename]={}

				if 'slow' in method:
					timeset['md5walk']['_parts'][setname][sourcename]['slow']={}
					timeset['md5walk']['_parts'][setname][sourcename]['slow']['start']=datetime.datetime.now()

					filelist.beginMD5Walk(targetpath+'/',logname,runopts['walkopts'])

					timeset['md5walk']['_parts'][setname][sourcename]['slow']['end']=datetime.datetime.now()
				if 'fast' in method:
					timeset['md5walk']['_parts'][setname][sourcename]['fast']={}
					timeset['md5walk']['_parts'][setname][sourcename]['fast']['start']=datetime.datetime.now()

					driveutils.makeMD5Fast(targetpath+'/',logname,runopts['walkopts'])

					timeset['md5walk']['_parts'][setname][sourcename]['fast']['end']=datetime.datetime.now()


				if '_errs' in runopts['walkopts'].keys():
					if '_folders' in runopts['walkopts']['_errs'].keys():
						if 'folderload' not in errset.keys():
							errset['folderload']={}
						if setname not in errset['folderload'].keys():
							errset['folderload'][setname]={}
						if sourcename not in errset['folderload'][setname].keys():
							errset['folderload'][setname][sourcename]=[]
						errset['folderload'][setname][sourcename].extend(runopts['walkopts']['_errs']['_folders'])

				driveutils.sortLogByPath(logname)
				loglist.append({'log':logname,'path':targetpath,'setname':setname,'sourcename':sourcename})
				logset[runname][setname][sourcename]=logname
				masterpath=logpath+'master/';	#	md5vali-master-
#				logset[name][setname]['master']=masterpath
				mastset[runname]=masterpath

#				print '---- b',setname,sourcename,startpath,logname
#				print '---- c',setname,sourcename,masterpath

	print
	print ' -- saved logs -- '
	for log in loglist:
		print log['log']
	print

	for log in loglist:
		driveutils.sortLogByPath(log['log'])

	newdata={}
	newdata['timestr'] = timestr
	newdata['logset'] = logset
	newdata['mastset'] = mastset
	newdata['loglist'] = loglist
	newdata['errset'] = errset
	if 'foldersets' in infosets.keys():
		newdata['targets'] = infosets['foldersets']

	return newdata

def splitMasterLog(masterlog,logfolder,tmpfolder,runname,timestamp,compopts):

	readname=compopts['readname']
	tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/';
	tmppath += 'sections/'

	masterpieces={}
	with open(masterlog) as masterfile:
	    for rline in masterfile.readlines():
			fpath = None
			groupsA = re.findall(r'^(?:[^,]+,){3}\s*(\/.*?\/\/.*\S)\s*$',rline)
			groupsB = re.findall(r'^((?:[^,]+,){3})\s*\/.*?\/\/.*\S\s*$',rline)
			fpath = groupsA[0]
			fdeets = groupsB[0]

			if re.match(r'^\/masterpath\/',fpath):
				groups1 = re.findall(r'^\/masterpath\/(.*?)\/\/.*$',fpath)
				setname=groups1[0]

				logpiece = tmppath+'/'+setname+'/masterpiece.txt'

				if not os.path.exists(logpiece):
					driveutils.createNewLog(logpiece,True)

				if setname not in masterpieces.keys():
					masterpieces[setname]={}
				if 'path' not in masterpieces[setname].keys():
					masterpieces[setname]['path']=logpiece
				if 'obj' not in masterpieces[setname].keys():
					masterpieces[setname]['obj']=open(logpiece,"a")

				masterpieces[setname]['obj'].write(rline)
	masterfile.close()

	for setname,mast in masterpieces.iteritems():
		if 'obj' in masterpieces[setname].keys():
			masterpieces[setname]['obj'].close()
			del masterpieces[setname]['obj']
		if 'path' in masterpieces[setname].keys():
			driveutils.sortLogByPath(masterpieces[setname]['path'])
	return masterpieces




def md5SourcesAndTargets(targetlist,runname,infosets,logfolder,tmpfolder,datasets,timeset,runopts=None):
	if runopts is None:
		runopts={}
	if 'compopts' not in runopts.keys():
		runopts['compopts']={}

	if runname in datasets['logset'].keys():

		timeset['splitlogs'] = {}
		timeset['splitlogs']['start'] = datetime.datetime.now()

		masterroute = datasets['mastset'][runname]

		if 'useold_md5log' in runopts['compopts'].keys() and 'logpath' in runopts['compopts']['useold_md5log'].keys():
			masterlog=runopts['compopts']['useold_md5log']['logpath']
			driveutils.sortLogByPath(masterlog)
		else:
			masterlog=grabAMasterLog(masterroute,datasets['timestr'],runopts['compopts'])
		driveutils.sortLogByPath(masterlog)
		masterlogset=splitMasterLog(masterlog,logfolder,tmpfolder,runname,datasets['timestr'],runopts['compopts'])

		timeset['compare'] = {}
		timeset['compare']['start'] = datetime.datetime.now()


		if runname in datasets['mastset'].keys():
			print '========================================='
			beginCompareStage(timeset,datasets['logset'][runname],runname,masterlogset,tmpfolder,datasets['mastset'][runname],datasets['timestr'],targetlist,datasets,runopts['compopts'])



def beginCompareStage(timeset,logsetlist,runname,masterlogset,tmpfolder,masterroute,timestamp,targetlist,datasets,compopts=None):
	if compopts is None:
		compopts={}
	compopts['_holddata']={}

	debuglog = masterroute+'master-'+timestamp+'/' + 'md5vali-debug-'+datasets['timestr']+'.txt'


	newmasterlog=masterroute+'master-'+timestamp+'/'
	newmasterlog+='md5vali-master-'+timestamp+'.txt'

	if 'useoutputlog' in compopts.keys():
		newmasterlog=compopts['useoutputlog']['logpath']



	##  Grab List of SetNames from datasets['logset'][runname]
	loglistkeys = logsetlist.keys()
	loglistkeys.sort()

	timeset['compare']['_parts'] = {}
	timeset['compare']['_parts']['_total'] = {}
	timeset['compare']['_parts']['_search'] = {}
	timeset['compare']['_parts']['_compare'] = {}
	for logsetname in loglistkeys:
		if logsetname == "_oldmaster" or logsetname == "newmaster":
			print "**** ERROR!! ****"
			print "Do not name any filesets '_oldmaster' or '_newmaster'"
			raise
			return

		if logsetname in masterlogset.keys():
			timeset['compare']['_parts']['_total'][logsetname] = {}

			timeset['compare']['_parts']['_total'][logsetname]['start'] = datetime.datetime.now()
			masterlog = masterlogset[logsetname]['path']
			comparedata.compareSourcesAndTargets(runname,timeset,masterlog,newmasterlog,timestamp,logsetlist[logsetname],logsetname,targetlist,tmpfolder,datasets,compopts)
			driveutils.sortLogByPath(newmasterlog+".tmp")
			timeset['compare']['_parts']['_total'][logsetname]['end'] = datetime.datetime.now()

	timeset['compare']['end'] = datetime.datetime.now()




	summarylog = masterroute+'md5vali-summary-'+timestamp+'.txt'
	driveutils.createNewLog(summarylog,True)



	movedlogpath=re.findall('^(.*)\/',newmasterlog)[0]+'/quicklists/moved-list-'+timestamp+'.txt'
	if os.path.exists(movedlogpath):
		print '----------------------------------------------'
		print
		driveutils.addToLog( "----------------------------------------------\n\n", summarylog )
		print '----------- master files moved -----------'
		driveutils.addToLog( "----------- master files moved -----------\n", summarylog )
		with open(movedlogpath) as f:
		    for rline in f.readlines():
				print rline.rstrip()
				driveutils.addToLog( rline.rstrip()+"\n", summarylog )


	print '----------------------------------------------'
	print
	driveutils.addToLog( "----------------------------------------------\n\n", summarylog )

	dropmissed.logMissedFolders(datasets,summarylog,compopts)

	os.rename(newmasterlog+".tmp",newmasterlog)
	driveutils.sortLogByPath(newmasterlog)

	sumlist={}
############################### BROKE AT HERE #######################################
	for runname,runset in compopts['_holddata']['totals'].iteritems():
		if runname not in sumlist.keys():
			sumlist[runname]={}
		for logsetname,logset in compopts['_holddata']['totals'][runname].iteritems():
			for sourcename,nameset in compopts['_holddata']['totals'][runname][logsetname].iteritems():
				if sourcename not in sumlist[runname].keys():
					sumlist[runname][sourcename]={}
				for tresult,val in nameset.iteritems():
					if tresult not in sumlist[runname][sourcename].keys():
						sumlist[runname][sourcename][tresult]=0
					sumlist[runname][sourcename][tresult]+=val



	if 'errset' in datasets.keys():
		if len( datasets['errset'].keys() ) > 0:
			print
			print '----------------errset-------------------'
			driveutils.addToLog( '\n----------------errset-------------------\n', summarylog )
			for typename,typelist in datasets['errset'].iteritems():
				print '------------------',typename,'-----------------------'
				driveutils.addToLog( '------------------'+typename+'-----------------------\n', summarylog )
				for item in typelist:
					print item
					driveutils.addToLog( item+'\n', summarylog )
			print '----------------------------------------------'
			driveutils.addToLog( '----------------------------------------------\n\n', summarylog )
			print



	print
	print '----------------------------------------------'
	print '-----------------totals-----------------------'
	driveutils.addToLog( "\n----------------------------------------------\n", summarylog )
	driveutils.addToLog( "-----------------totals-----------------------\n", summarylog )

	for runname,runset in compopts['_holddata']['totals'].iteritems():
		for logsetname,logset in compopts['_holddata']['totals'][runname].iteritems():
			for sourcename,nameset in compopts['_holddata']['totals'][runname][logsetname].iteritems():
				strr=""
				for tresult,val in nameset.iteritems():
					strr=strr+tresult+"="+str(val)+'  '
				print ' - totals: ',runname,'-',logsetname,'-',sourcename,' : '+strr.rstrip()
				driveutils.addToLog( ' - totals:  '+runname+' - '+logsetname+' - '+sourcename+'  :  '+strr.rstrip()+"\n", summarylog )
#			compopts['_holddata']['totals'][runname][logsetname][tname][tresult]+=1
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
	for tresult,val in compopts['_holddata']['overalltotals'].iteritems():
		strr=strr+tresult+': '+str(val)+',   '
	print ' - sets:   ',(strr.rstrip())[0:-1]
	strr=(strr.rstrip())[0:-1]
	driveutils.addToLog( ' - sets:    '+strr+"\n", summarylog )
	print '----------------------------------------------'
	driveutils.addToLog( "----------------------------------------------\n", summarylog )






	duration_md5 = timeset['md5walk']['end'] - timeset['md5walk']['start']
	duration_split = timeset['splitlogs']['end'] - timeset['splitlogs']['start']
	duration_run = timeset['compare']['end'] - timeset['compare']['start']

	duration_md5arr = []
	if '_parts' in timeset['md5walk'].keys():
		for setname,setitem in timeset['_md5sets'].iteritems():
			for sourcename,setitem2 in timeset['_md5sets'][setname].iteritems():
				for pace,setitem3 in timeset['_md5sets'][setname][sourcename].iteritems():
					s = timeset['_md5sets'][setname][sourcename][pace]['start']
					e = timeset['_md5sets'][setname][sourcename][pace]['end']
					duration_md5arr.append({'setname':setname,'sourcename':sourcename,'pace':pace,'time':(e-s)})
	duration_md5arr2 = []
	if '_parts' in timeset['compare'].keys():
		for typename,setitem in timeset['compare'].iteritems():
			for setname,setitem2 in timeset['compare'][typename].iteritems():
				s = timeset['compare'][typename][setname]['start']
				e = timeset['compare'][typename][setname]['end']
				duration_md5arr2.append({'typename':typename,'setname':setname,'time':(e-s)})



	print '----------------------------------------------'
	print "\nMD5 Time: ",str(duration_md5)
	if (len(duration_md5arr) > 0):
		for dur in duration_md5arr:
			print " - MD5 dur stop: "+dur['setname']+","+dur['sourcename']+": "+str(dur['time'])
	print '----------------------------------------------'
	print "Compare Time: ",str(duration_run)
	if (len(duration_md5arr2) > 0):
		for dur in duration_md5arr2:
			print " - compare dur stop: "+dur['typename']+","+dur['setname']+": "+str(dur['time'])
	print '----------------------------------------------'
	print "\nMD5 Time: ",str(duration_md5)
	print "Split Time: ",str(duration_split)
	print "Compare Time: ",str(duration_run),"\n"


	driveutils.addToLog( "----------------------------------------------\n", summarylog )
	driveutils.addToLog( "MD5 Duration: "+str(duration_md5)+"\n", summarylog )
	if (len(duration_md5arr) > 0):
		for dur in duration_md5arr:
			driveutils.addToLog( " - MD5 dur stop: "+dur['setname']+","+dur['sourcename']+":"+dur['pace']+": "+str(dur['time'])+"\n", summarylog )
	driveutils.addToLog( "----------------------------------------------\n", summarylog )
	driveutils.addToLog( "Compare Duration: "+str(duration_run)+"\n", summarylog )
	if (len(duration_md5arr2) > 0):
		for dur in duration_md5arr2:
			driveutils.addToLog( " - compare dur stop: "+dur['typename']+","+dur['setname']+": "+str(dur['time'])+"\n", summarylog )
	driveutils.addToLog( "----------------------------------------------\n", summarylog )
	driveutils.addToLog( "MD5 Duration: "+str(duration_md5)+"\n", summarylog )
	driveutils.addToLog( "Split Duration: "+str(duration_split)+"\n", summarylog )
	driveutils.addToLog( "Compare Duration: "+str(duration_run)+"\n", summarylog )


#			compopts['_holddata']['overalltotals'][grouptype]=0
	compopts['_holddata']['overalltotals']={}
	print '\n - summarized in:  ',summarylog
	print '\n - logged in:  ',newmasterlog


def logAndCompTargets(targetlist, logfolder,tmpfolder, runopts=None):
	if runopts is None:
		runopts={}

	timestr = time.strftime("%Y%m%d-%H%M%S")
	mountlist = findmounts.getMounts()

	for runname,infosets in targetlist.iteritems():
		if 'file' in infosets.keys():
			foundlist = findmounts.findTargetsInMounts(mountlist, infosets['file'])

		timeset={}

		readname=runopts['compopts']['readname']
		if 'justdropmissing' in runopts['compopts'].keys():
			masterroute = logfolder+'/md5vali/'+readname+'/'+runname+'/master/'
			if 'useold_md5log' in runopts['compopts'].keys() and 'logpath' in runopts['compopts']['useold_md5log'].keys():
				masterlog=runopts['compopts']['useold_md5log']['logpath']
			else:
				masterlog=grabAMasterLog(masterroute,timestr,runopts['compopts'])

			print 'xxx',masterlog
			masterlogtime = (re.findall(r'-master-(\d+-\d+)\.txt\s*$',masterlog)[0])
			masterlogpath = (re.findall(r'^(\/.*\/)[^\/]+\.txt\s*$',masterlog)[0])
			missinglist = masterlogpath+'quicklists/missing-list-'+masterlogtime+'.txt'
			if os.path.exists(missinglist):
				dropmissed.dropMissing(masterlog,missinglist,timestr, masterroute)
				return
			return


		timeset['md5walk'] = {}
		timeset['md5walk']['start'] = datetime.datetime.now()

		tmplogs.clearTmpMD5Logs('md5vali',runname,logfolder)
		datasets = createNewTmpMD5Logs(runname,timestr,infosets,foundlist,logfolder,tmpfolder,timeset,runopts)

		timeset['md5walk']['end'] = datetime.datetime.now()

		if len(datasets.keys()) > 0:
			datasets['found']=foundlist

			md5SourcesAndTargets(targetlist,runname,infosets,logfolder,tmpfolder,datasets,timeset,runopts)


		tmparr=['pieces', 'sections']
		readname=runopts['compopts']['readname']
		tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestr+'/';
		logpath = logfolder+'/md5vali/'+readname+'/'+runname+'/';

		for tmp in tmparr:
			l = logpath+tmp
			l2 = tmppath+tmp
			if os.path.exists(l):
				shutil.rmtree(l)
			shutil.copytree(l2,l)

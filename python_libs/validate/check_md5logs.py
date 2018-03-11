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



def grabAMasterLog(masterpath,timestamp,useopts):
	masterlog = getBestMaster(masterpath, useopts)
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

def getBestMaster(masterpath,useopts):
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

def createNewTmpMD5Logs(runname,timestr,infosets,foundlist,logfolder,tmpfolder,timeset,md5opts=None):
	if md5opts is None:
		md5opts={}
	if 'walkopts' not in md5opts.keys():
		md5opts['walkopts']={}

	logset={}
	mastset={}
	errset={}
	loglist=[]

	if runname not in logset.keys():
		logset[runname]={}
	logpath = logfolder+'/md5vali/'+runname+'/';
	tmppath = tmpfolder+'/md5vali/'+runname+'/'+timestr+'/';

	timeset['_md5sets'] ={}

	if 'usenew_md5log' in md5opts['walkopts'].keys():

		uselog=md5opts['walkopts']['usenew_md5log']['logpath']
		if os.path.exists(uselog) and os.path.isfile(uselog):
			print "Using ",uselog
			driveutils.sortLogByPath(uselog)

			if 'foldersets' in infosets.keys():
				for setname,folderset in infosets['foldersets'].iteritems():
					for sourcename,folderpath in folderset.iteritems():

						if sourcename != md5opts['walkopts']['usenew_md5log']['setsource']:
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
				if 'method' in md5opts['walkopts'].keys():
					method=[]
					if 'slow' in md5opts['walkopts']['method'].keys():
						if setname in md5opts['walkopts']['method']['slow']:
							method.append['slow']
					if 'fast' in md5opts['walkopts']['method'].keys():
						if setname in md5opts['walkopts']['method']['fast']:
							method.append['fast']
				if len(method) == 0:
					method=['fast']

				timeset['_md5sets'][setname]={}
				timeset['_md5sets'][setname][sourcename]={}

				if 'slow' in method:
					timeset['_md5sets'][setname][sourcename]['slow']={}
					timeset['_md5sets'][setname][sourcename]['slow']['start']=datetime.datetime.now()

					filelist.beginMD5Walk(targetpath+'/',logname,md5opts['walkopts'])

					timeset['_md5sets'][setname][sourcename]['slow']['end']=datetime.datetime.now()
				if 'fast' in method:
					timeset['_md5sets'][setname][sourcename]['fast']={}
					timeset['_md5sets'][setname][sourcename]['fast']['start']=datetime.datetime.now()

					driveutils.makeMD5Fast(targetpath+'/',logname,md5opts['walkopts'])

					timeset['_md5sets'][setname][sourcename]['fast']['end']=datetime.datetime.now()


				if '_errs' in md5opts['walkopts'].keys():
					if '_folders' in md5opts['walkopts']['_errs'].keys():
						if 'folderload' not in errset.keys():
							errset['folderload']={}
						if setname not in errset['folderload'].keys():
							errset['folderload'][setname]={}
						if sourcename not in errset['folderload'][setname].keys():
							errset['folderload'][setname][sourcename]=[]
						errset['folderload'][setname][sourcename].extend(md5opts['walkopts']['_errs']['_folders'])

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

def splitMasterLog(masterlog,logfolder,tmpfolder,runname,timestamp):
	tmppath = tmpfolder+'/md5vali/'+runname+'/'+timestamp+'/';
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




def md5SourcesAndTargets(targetlist,runname,infosets,logfolder,tmpfolder,datasets,timeset,md5opts=None):
	if md5opts is None:
		md5opts={}
	if 'compopts' not in md5opts.keys():
		md5opts['compopts']={}

	if runname in datasets['logset'].keys():

		masterroute = datasets['mastset'][runname]

		if 'useold_md5log' in md5opts['compopts'].keys() and 'logpath' in md5opts['compopts']['useold_md5log'].keys():
			masterlog=md5opts['compopts']['useold_md5log']['logpath']
			driveutils.sortLogByPath(masterlog)
		else:
			masterlog=grabAMasterLog(masterroute,datasets['timestr'],md5opts['compopts'])
		driveutils.sortLogByPath(masterlog)
		masterlogset=splitMasterLog(masterlog,logfolder,tmpfolder,runname,datasets['timestr'])

		timeset['postsplit'] = datetime.datetime.now()

		if runname in datasets['mastset'].keys():
			print '========================================='
			beginCompareStage(timeset,datasets['logset'][runname],runname,masterlogset,tmpfolder,datasets['mastset'][runname],datasets['timestr'],targetlist,datasets,md5opts['compopts'])



def beginCompareStage(timeset,logsetlist,runname,masterlogset,tmpfolder,masterroute,timestamp,targetlist,datasets,useopts=None):
	if useopts is None:
		useopts={}
	useopts['_holddata']={}

	debuglog = masterroute+'master-'+timestamp+'/' + 'md5vali-debug-'+datasets['timestr']+'.txt'


	newmasterlog=masterroute+'master-'+timestamp+'/'
	newmasterlog+='md5vali-master-'+timestamp+'.txt'

	if 'useoutputlog' in useopts.keys():
		newmasterlog=useopts['useoutputlog']['logpath']




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
			comparedata.compareSourcesAndTargets(runname,masterlog,newmasterlog,timestamp,logsetlist[logsetname],logsetname,targetlist,tmpfolder,datasets,useopts)
			driveutils.sortLogByPath(newmasterlog+".tmp")


	timeset['postrun'] = datetime.datetime.now()

	duration_md5 = timeset['postmd5'] - timeset['premd5']
	duration_split = timeset['postsplit'] - timeset['postmd5']
	duration_run = timeset['postrun'] - timeset['postsplit']

	duration_md5arr = []
	if '_md5sets' in timeset.keys():
		for setname,setitem in timeset['_md5sets'].iteritems():
			for sourcename,setitem2 in timeset['_md5sets'][setname].iteritems():
				for pace,setitem3 in timeset['_md5sets'][setname][sourcename].iteritems():
					s = timeset['_md5sets'][setname][sourcename][pace]['start']
					e = timeset['_md5sets'][setname][sourcename][pace]['end']
					duration_md5arr.append({'setname':setname,'sourcename':sourcename,'pace':pace,'time':(e-s)})



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

	dropmissed.logMissedFolders(datasets,summarylog,useopts)

	os.rename(newmasterlog+".tmp",newmasterlog)
	driveutils.sortLogByPath(newmasterlog)

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
	print '----------------------------------------------'
	driveutils.addToLog( "----------------------------------------------\n", summarylog )


	print "\nMD5 Time: ",str(duration_md5)
	if (len(duration_md5arr) > 0):
		for dur in duration_md5arr:
			print " - MD5 dur stop: "+dur['setname']+","+dur['sourcename']+": "+str(dur['time'])
	print "Split Time: ",str(duration_split)
	print "Check Time: ",str(duration_run),"\n"


	driveutils.addToLog( "MD5 Duration: "+str(duration_md5)+"\n", summarylog )
	if (len(duration_md5arr) > 0):
		for dur in duration_md5arr:
			driveutils.addToLog( " - MD5 dur stop: "+dur['setname']+","+dur['sourcename']+":"+dur['pace']+": "+str(dur['time'])+"\n", summarylog )
	driveutils.addToLog( "Split Duration: "+str(duration_split)+"\n", summarylog )
	driveutils.addToLog( "Check Duration: "+str(duration_run)+"\n", summarylog )


#			useopts['_holddata']['overalltotals'][grouptype]=0
	useopts['_holddata']['overalltotals']={}
	print '\n - summarized in:  ',summarylog
	print '\n - logged in:  ',newmasterlog


def logAndCompTargets(targetlist, logfolder,tmpfolder, md5opts=None):
	if md5opts is None:
		md5opts={}

	timestr = time.strftime("%Y%m%d-%H%M%S")
	mountlist = findmounts.getMounts()

	for runname,infosets in targetlist.iteritems():
		if 'file' in infosets.keys():
			foundlist = findmounts.findTargetsInMounts(mountlist, infosets['file'])

		timeset={}
		timeset['premd5'] = datetime.datetime.now()

		if 'justdropmissing' in md5opts['compopts'].keys():
			masterroute = logfolder+'/md5vali/'+runname+'/master/'
			if 'useold_md5log' in md5opts['compopts'].keys() and 'logpath' in md5opts['compopts']['useold_md5log'].keys():
				masterlog=md5opts['compopts']['useold_md5log']['logpath']
			else:
				masterlog=grabAMasterLog(masterroute,timestr,md5opts['compopts'])

			print 'xxx',masterlog
			masterlogtime = (re.findall(r'-master-(\d+-\d+)\.txt\s*$',masterlog)[0])
			masterlogpath = (re.findall(r'^(\/.*\/)[^\/]+\.txt\s*$',masterlog)[0])
			missinglist = masterlogpath+'quicklists/missing-list-'+masterlogtime+'.txt'
			if os.path.exists(missinglist):
				dropmissed.dropMissing(masterlog,missinglist,timestr, masterroute)
				return
			return

		tmplogs.clearTmpMD5Logs('md5vali',runname,logfolder)
		datasets = createNewTmpMD5Logs(runname,timestr,infosets,foundlist,logfolder,tmpfolder,timeset,md5opts)

		timeset['postmd5'] = datetime.datetime.now()

		if len(datasets.keys()) > 0:
			datasets['found']=foundlist

			md5SourcesAndTargets(targetlist,runname,infosets,logfolder,tmpfolder,datasets,timeset,md5opts)


		tmparr=['pieces', 'sections']
		tmppath = tmpfolder+'/md5vali/'+runname+'/'+timestr+'/';
		logpath = logfolder+'/md5vali/'+runname+'/';

		for tmp in tmparr:
			l = logpath+tmp
			l2 = tmppath+tmp
			if os.path.exists(l):
				shutil.rmtree(l)
			shutil.copytree(l2,l)

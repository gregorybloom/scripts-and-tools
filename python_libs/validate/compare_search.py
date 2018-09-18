
from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import datetime
import json
from sys import version_info

#	test "DROP OLD" and "ASK DROP OLD"
#	test "DELETE LAST"

# #	FIND MOVED FILES
# runname,logsetname,sourcename,md5,{from:_,to:_}
#
# search stage:
#	if new or missing:
#		add to a check log (tmp---runname,logssetname,sourcename,new/missing,timestamp,.txt)
#
# build movelog:
#	search for run,set,source,md5 match
#	find best fit:
#		same folder: lowest changed characters
#		diff folder: *************
#   save best fit "runname,logsetname,sourcename,md5,{from:_,to:_}"
#   delete used entries from both logs
# uniquify sort
#
# compare stage:
#	if new && in log && oldmaster.state == missing && path == "to:"
#		skip?
#	if missing && in log && oldmaster.state == present && path == "from:"
#		create moved master line
#		print "moved from" for source
#		print "moved to" for source

def searchSourcesAndTargets(readname,runname,masterlog,newmasterlog,timestamp,logset,logsetname,targetlist,tmpfolder,datasets,useopts=None):
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

	masterlist={}

	masterlist['_oldmaster']={}
	logBf = open(masterlog, 'rb')
	masterlist['_oldmaster']['obj']=logBf
	masterlist['_oldmaster']['pos']=0
	masterlist['_oldmaster']['logpath']=masterlog



	tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/miss-search/';


	masterlist['_newmaster']={}
	masterlist['_newmaster']['newpath']=re.findall('^(.*)\/',newmasterlog)[0]
	masterlist['_newmaster']['newtime']=timestamp

	for sourcename,logpath in logset.iteritems():
		tmppath2 = tmppath+ 'missing/'+logsetname+'/missing-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'
		tmppath3 = tmppath+ 'new/'+logsetname+'/new-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'
		masterlist['_newmaster'][sourcename]={}
		masterlist['_newmaster'][sourcename]['miss']={}
		masterlist['_newmaster'][sourcename]['new']={}
		masterlist['_newmaster'][sourcename]['miss']['logpath'] = tmppath2
		masterlist['_newmaster'][sourcename]['new']['logpath'] = tmppath3
		driveutils.createNewLog(tmppath2,True)
		driveutils.createNewLog(tmppath3,True)
		masterlist['_newmaster'][sourcename]['miss']['obj'] = open(tmppath2, 'ab')
		masterlist['_newmaster'][sourcename]['new']['obj'] = open(tmppath3, 'ab')
	#####################################

	c=0
	opath=''
	useopts['firstrun']=True
	while True:
		col=stepSearchLogs(c,steplist,masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)
		useopts['firstrun']=False
		if(opath == col['lowest'] and c>0):
			break
		if(col['lowest'] is None and col['count'] is None):
			break
		c=col['count']
		opath=col['lowest']



	comparefns.closeUpFiles(steplist)
	comparefns.closeUpFiles(masterlist)

	for sourcename,logpath in logset.iteritems():
		tmppath2 = tmppath+ 'missing/'+logsetname+'/missing-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'
		tmppath3 = tmppath+ 'new/'+logsetname+'/new-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'
		masterlist['_newmaster'][sourcename]['miss']['obj'].close()
		masterlist['_newmaster'][sourcename]['new']['obj'].close()

	return
	#####################################
	for sourcename,logobj in masterlist['_newmaster'].iteritems():
		for ftype in ['miss','new']:
			if isinstance(masterlist['_newmaster'][sourcename],dict):
				if ftype in masterlist['_newmaster'][sourcename].keys():
					if 'obj' in masterlist['_newmaster'][sourcename][ftype].keys():
						masterlist['_newmaster'][sourcename][ftype]['obj'].close()
					if 'logpath' in masterlist['_newmaster'][sourcename][ftype].keys():
						driveutils.sortLogByPath(masterlist['_newmaster'][sourcename][ftype]['logpath'])


def stepSearchLogs(c,steplist,masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts=None):
	if useopts is None:
		useopts={}

	comparefns.loadStepList(steplist,useopts)
	comparefns.prepStepListVals(steplist,readname,runname,logsetname,tmpfolder,datasets,useopts)

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
		for i,item in steplist.iteritems():
			print ' s,:',i,item

	comparefns.loadStepList(masterlist,useopts)
	comparefns.prepStepListVals(masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
		for i,item in steplist.iteritems():
			print ' s_:',i,item

	# DEFUNCT?
	comparefns.pushMasterListToGroup(masterlist,readname,runname,logsetname,tmpfolder,datasets,useopts)


	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		for i,item in steplist.iteritems():
			print ' s..:',i,item['cur_mtype'],item['cur_bsize'],item['cur_sha'],item['cur_path'],item['hashes']
		for i,item in masterlist.iteritems():
			if i != '_newmaster':
				print ' s..:',i,item['cur_mtype'],item['cur_bsize'],item['cur_sha'],item['cur_path'],item['hashes']

	matches = {}
	comparefns.comparePathsInLogSet(matches,steplist,useopts)
	comparefns.comparePathsInLogSet(matches,masterlist,useopts)

#		print
	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		for i,item in matches.iteritems():
			print ' s:',i,item

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

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		for i,item in compSET["_sources"].iteritems():
			print ' s%',i,item['state'],item['cur_sha'],item['cur_mtype'],item['cur_path']

	comparefns.summarizeCompSet(lowest,matches,compSET,steplist,logsetname,datasets)

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		for i,item in compSET["_summary"].iteritems():
			print ' s>',i,item



	matchnames = writeMoveOptions(compSET,masterlist['_newmaster'],readname,runname,logsetname,steplist,masterlist,tmpfolder,datasets,useopts)

	outputxt = 'precheck # '+str(c)+' ! '+logsetname+', '+lowest+' ! '+compSET["_summary"]['pstate']+', '+compSET["_summary"]['sstate']+', '+str(matchnames)
	print outputxt

	comparefns.incrementPtrs(compSET['_summary']['compset'],steplist,useopts)
	comparefns.incrementPtrs(compSET['_summary']['compset'],masterlist,useopts)

	if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
		print '----------------------------------------------'
		print '----------------------------------------------'
	return {'count':c+1,'lowest':lowest}




def	writeMoveOptions(compSET,newlog,readname,runname,logsetname,steplist,masterlist,tmpfolder,datasets,useopts=None):
	if useopts is None:
		useopts={}
	if '_holddata' not in useopts.keys():
		useopts['_holddata']={}


	timestamp = masterlist['_newmaster']['newtime']

	if compSET['_summary']['masterstate'] != 'missing':

		masterfilepath = "/masterpath/"+logsetname+'/'+compSET['_summary']['path']

		masterfiledata = None
		if 'line' in compSET['_oldmaster'].keys():
			relook=re.findall(r'^(\w+,\s*\d+,[^,]+,\s*)\/',compSET['_oldmaster']['line'])
			if len(relook)>0:
				masterfiledata = relook[0]
		if masterfiledata is not None:
			masterline = masterfiledata+masterfilepath+"\n"
			compSET['_summary']['masterline']=masterline.rstrip()

			for sourcename,sourceobj in compSET['_sources'].iteritems():
				tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/miss-search/';

				if sourceobj['state'] == 'missing':
					hashes={}
					hashes[ compSET['_summary']['mtype'] ]=compSET['_summary']['sha']

					outline = runname+','+logsetname+','+sourcename+',missing,'+compSET['_summary']['sha']+','+compSET['_summary']['bsize']+',mtype:'+compSET['_summary']['mtype']+','
					outline += json.dumps({'path':compSET['_summary']['path'],'hashes':hashes})

					masterlist['_newmaster'][sourcename]['miss']['obj'].write(outline+"\n")

	elif compSET['_summary']['masterstate'] == 'missing':
		for sourcename,sourceobj in compSET['_sources'].iteritems():
			tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/miss-search/';

			if sourceobj['state'] == 'new':

				count = None
				if 'useblocks' in useopts.keys() and '_count' in useopts['useblocks'].keys():
					count = int(useopts['useblocks']['_count'])
				test=['md5','sha1']
				hashes={}
				hashes[ compSET['_sources'][sourcename]['cur_mtype'] ]=compSET['_sources'][sourcename]['cur_sha']
				for t in test:
					if t not in hashes.keys():
						basepath=comparefns.grabBasePath(logsetname,sourcename,datasets)
						thepath=basepath.rstrip('/')+"/"+compSET['_sources'][sourcename]['cur_path']
						if 'verbose' in useopts.keys() and useopts['verbose'] >= 2:
							print 'getsha - masterstate:missing,',sourcename,sourceobj,t,compSET['_sources'][sourcename]['cur_path'],compSET['_sources'][sourcename]
						hashes[t]=driveutils.shaSum(thepath,count,t)
				compSET['_sources'][sourcename]['hashes']=hashes

				outline = runname+','+logsetname+','+sourcename+',new,'+compSET['_sources'][sourcename]['cur_sha']+','+compSET['_sources'][sourcename]['cur_bsize']+',mtype:'+compSET['_sources'][sourcename]['cur_mtype']+','
				outline += json.dumps({'path':compSET['_sources'][sourcename]['cur_path'],'hashes':hashes})

#				print compSET['_summary']['path'],sourcename,outline
				masterlist['_newmaster'][sourcename]['new']['obj'].write(outline+"\n")


	for sourcename,sourceobj in compSET['_sources'].iteritems():
		if len(compSET['_sources'][sourcename]['cur_path']) < 2:
			continue

		tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/newcalc/';

		tmppath2 = tmppath+'/newcalc-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'
		driveutils.createNewLog(tmppath2,True)
		newcalclog = open(tmppath2, 'ab')

		if 'hashes' in compSET['_sources'][sourcename].keys():
			if len( compSET['_sources'][sourcename]['hashes'].keys() ) > 1:
				recalcobj={}
				recalcobj['path']=compSET['_sources'][sourcename]['cur_path']
				recalcobj['hashes']=compSET['_sources'][sourcename]['hashes']

				writeline = json.dumps(recalcobj)

				newcalclog.write(writeline+"\n")
		newcalclog.close()

def grabFromNewCalcs(steplist,name,readname,runname,logsetname,sourcename,tmpfolder,useopts=None):
	timestamp = useopts['timestamp']
	tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/newcalc/';
	tmppath2 = tmppath+'/newcalc-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'

	if steplist[name]['cur_path'] is None or len(steplist[name]['cur_path']) < 2:
		return

	if os.path.exists(tmppath2):
		with open(tmppath2,'rb') as f:
		    for rline in f.readlines():
				if re.match('^\{.*\}\s*$',rline):
					outobj = json.loads(rline)

					if steplist[name]['cur_path'] < outobj['path']:
						continue
					if steplist[name]['cur_path'] > outobj['path']:
						return
					if steplist[name]['cur_mtype'] in outobj['hashes'].keys():
						mcheck = steplist[name]['cur_mtype']
						if steplist[name]['cur_sha'] != outobj['hashes'][mcheck]:
							continue
					else:
						totalmtypes=[]
						totalmtypes.extend( outobj['hashes'].keys() )
						totalmtypes.extend( steplist[name]['hashes'].keys() )
						mysettypes = set(totalmtypes)
						mysetarray = list(mysettypes)
						if len(mysetarray) == 0:
							continue
						sharearray=list(set(outobj['hashes'].keys()).intersection(steplist[name]['hashes'].keys()))
						if len(sharearray) == 0:
							continue

						breakout=False
						for myset in mysetarray:
							if myset in steplist[name]['hashes'].keys() and myset in outobj['hashes'].keys():
								if steplist[name]['hashes'][myset] != outobj['hashes'][myset]:
									breakout=True
									break
						if breakout:
							continue

						for myset in mysetarray:
							if myset not in steplist[name]['hashes'].keys() and myset in outobj['hashes'].keys():
								steplist[name]['hashes'][myset] = outobj['hashes'][myset]
						return
	#				print outobj


def getBestFitPossible(outpath,moveobj,possible_fits):
	opath= re.sub(r"\/\/", "/", outpath)
	pathset=opath.split('/')
	pathset.reverse()
	fitcheck=[]
	countfit=0
	for fitobj in possible_fits:
		if outpath == fitobj['path']:
#			print "MAAAAAAAAAAAAAATCHES"
			newobj={}
			newobj['highest']=-1
			newobj['count']=countfit
			newobj['diffpts']=[-1]
			return newobj

		fpath = re.sub(r"\/\/", "/", fitobj['path'])
		fpathset=fpath.split('/')
		fpathset.reverse()
		############################ FIX THIS!  WHAT HAPPENS IF IT WAS MOVED INTO A SUBFOLDER?
		newfitobj={}
		newfitobj['diffpts']=[]
		m = max(len(pathset),len(fpathset))
		for c in range(0,m):
			if c < len(pathset) and c < len(fpathset) and pathset[c] == fpathset[c]:
				continue
			newfitobj['diffpts'].append(c)
#		print pathset,'==',fpathset,':',newfitobj['diffpts']
		if len(newfitobj['diffpts']) > 0:
			newfitobj['highest']=newfitobj['diffpts'][-1]
		else:
			newfitobj['highest']=-1
		newfitobj['count']=countfit
		fitcheck.append(newfitobj)
		countfit+=1
	bestnum=999
	for fitobj in fitcheck:
		if fitobj['highest'] < bestnum:
			bestnum=fitobj['highest']
	nextarr=[]
	for fitobj in fitcheck:
		if fitobj['highest'] == bestnum:
			nextarr.append(fitobj)
	if len(nextarr) == 0:
		return None
	if len(nextarr) == 1:
		return nextarr[0]
	#### IMPROVE THIS LATER
	return nextarr[0]

def	buildMoveLog(readname,runname,timestamp,logset,logsetname,tmpfolder,datasets,useopts=None):
	tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/miss-search/';

	for sourcename,logpath in logset.iteritems():
		movedpath = tmppath+ 'moved/'+logsetname+'/moved-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'

		driveutils.createNewLog(movedpath,True)
		movedlog = open(movedpath, 'ab')

		tmppath2 = tmppath+ 'missing/'+logsetname+'/missing-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'
		tmppath3 = tmppath+ 'new/'+logsetname+'/new-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'

		if os.path.exists(tmppath2) and os.path.exists(tmppath3):
			if os.path.exists(tmppath3+".ext"):
				os.remove(tmppath3+".ext")
			shutil.copy(tmppath3,tmppath3+".ext")

			c = 0
			with open(tmppath2,'rb') as f:
			    for rline in f.readlines():
					moveobj = {}

					outrunname = re.findall('^([^,]*),\s*',rline)[0]
					outlogsetname = re.findall('^(?:[^,]*,\s*){1}([^,]*),',rline)[0]
					outsourcename = re.findall('^(?:[^,]*,\s*){2}([^,]*),missing,\s*',rline)[0]
					outsha = re.findall('^(?:[^,]*,\s*){3}missing,\s*([^,]*),',rline)[0]
					outbsize = re.findall('^(?:[^,]*,\s*){5}\s*([^,]*),',rline)[0]
					outdatastr = re.findall('^(?:[^,]*,\s*){6}\s*([^,]*),',rline)[0]
					outobjstr = re.findall('^(?:[^,]*,\s*){7}(\{.*\})\s*$',rline)[0]

					outdata = driveutils.decomposeFileLogItemData(outdatastr)
					if 'mtype' in outdata:
						outmtype = outdata['mtype']


					if runname != outrunname or logsetname != outlogsetname or sourcename != outsourcename:
						continue

					outobj = json.loads(outobjstr)
					outpath = outobj['path']
					outhashes = outobj['hashes']

					moveobj['runname'] = outrunname
					moveobj['logsetname'] = outlogsetname
					moveobj['sourcename'] = outsourcename
					moveobj['sha'] = outsha
					moveobj['bsize'] = outbsize
					moveobj['mtype'] = outmtype
					moveobj['line'] = outrunname+','+outlogsetname+','+outsourcename+','+outsha+','+outbsize+', mtype:'+outmtype+','

#					if re.match(r'^.*DiscordChatExporter.zip.*',outpath):
#						print '~~==',moveobj['line'],outobj

					possible_fits=[]
					c2 = 0
#					print '------'
#					print '.',outsha,outpath
					with open(tmppath3+".ext",'rb') as f2:
					    for rline2 in f2.readlines():

							inrunname = re.findall('^([^,]*),\s*',rline2)[0]
							inlogsetname = re.findall('^(?:[^,]*,\s*){1}([^,]*),',rline2)[0]
							insourcename = re.findall('^(?:[^,]*,\s*){2}([^,]*),new,\s*',rline2)[0]
							insha = re.findall('^(?:[^,]*,\s*){3}new,\s*([^,]*),',rline2)[0]
							inbsize = re.findall('^(?:[^,]*,\s*){5}\s*([^,]*),',rline2)[0]
							indatastr = re.findall('^(?:[^,]*,\s*){6}\s*([^,]*),',rline2)[0]

							indata = driveutils.decomposeFileLogItemData(indatastr)
							if 'mtype' in indata:
								inmtype = indata['mtype']


							inobjstr = re.findall('^(?:[^,]*,\s*){7}(\{.*\})\s*$',rline2)[0]
#							if re.match(r'^.*DiscordChatExporter.zip.*',outpath):
#								print '~~==  ..',inobjstr,outbsize,' != ',inbsize,',',outsha,' != ',insha,' and ',outmtype,' == ',inmtype
							if runname != inrunname or logsetname != inlogsetname or sourcename != insourcename:
								continue
#							print outsha,'==',insha
							if outbsize != inbsize:
								continue
							if outsha != insha and outmtype == inmtype:
								continue
							inobj = json.loads(inobjstr)
							inpath = inobj['path']
							inhashes = inobj['hashes']

#							if re.match(r'^.*DiscordChatExporter.zip.*',inpath):
#								print '~~== !!',inobj,indatastr
#								print '~~== !! 1)',outsha,' != ',insha,' or ',outmtype,' != ',inmtype
#								print '~~== !! 2)',useopts['mtype'],' not in ',outhashes.keys()
#								print '~~== !! 3)',useopts['mtype'],' not in ',inhashes.keys()
#								print '~~== !! 4)',useopts['mtype'],',',outhashes,' != ',inhashes

							if outsha != insha or outmtype != inmtype:
#								if re.match(r'^.*DiscordChatExporter.zip.*',inpath):
#									print '~~== @@a',inobj,indatastr
								if 'mtype' not in useopts.keys():
									continue
#								if re.match(r'^.*DiscordChatExporter.zip.*',inpath):
#									print '~~== @@b',inobj,indatastr
#								if useopts['mtype'] not in outhashes.keys():
#									continue
#								if re.match(r'^.*DiscordChatExporter.zip.*',inpath):
#									print '~~== @@c',inobj,indatastr
								if useopts['mtype'] not in inhashes.keys():
									continue
#								if re.match(r'^.*DiscordChatExporter.zip.*',inpath):
#									print '~~== @@d',inobj,indatastr
								totalmtypes=[]
								totalmtypes.extend( outhashes.keys() )
								totalmtypes.extend( inhashes.keys() )
								mysettypes = set(totalmtypes)
								mysetarray = list(mysettypes)
								if len(mysetarray) == 0:
									continue
								sharearray=list(set(outhashes.keys()).intersection(inhashes.keys()))
								if len(sharearray) == 0:
									continue

								breakout=False
								for myset in mysetarray:
									if myset in outhashes.keys() and myset in inhashes.keys():
										if outhashes[myset] != inhashes[myset]:
											breakout=True
											break
								if breakout:
									continue

								for myset in mysetarray:
									if myset not in outhashes.keys() and myset in inhashes.keys():
										outhashes[myset] = inhashes[myset]
									if myset not in inhashes.keys() and myset in outhashes.keys():
										inhashes[myset] = outhashes[myset]

#							if re.match(r'^.*DiscordChatExporter.zip.*',inpath):
#								print '~~== @@@@@',inobj,indatastr
							possible_fits.append({'path':inpath,'line':rline2,'count':c2})
							c2+=1
					if len(possible_fits) == 0:
						continue

					best_fit = None
					if len(possible_fits) == 1:
						best_fit = possible_fits[0]
					else:
						best_fit_obj = getBestFitPossible(outpath,moveobj,possible_fits)
						if 'highest' in best_fit_obj.keys():
							count = best_fit_obj['count']
							if count < len(possible_fits) and count >= 0:
								best_fit = possible_fits[count]
#						print '!'
#						for poss in possible_fits:
#							print '--',poss
#						print best_fit_obj,best_fit
#						print '!'
					if best_fit is None:
						continue

					moveline = outrunname+','+outlogsetname+','+outsourcename+','+outsha+','+outbsize+','+outmtype+','
					moveaddobj = {}
					moveaddobj['from']=outpath
					moveaddobj['to']=best_fit['path']
					moveaddobj['hashes']=outhashes
					moveline += json.dumps(moveaddobj)

					movedlog.write(moveline+"\n")

					### REWRITE tmppath3 w/o bestfit to .tmp and replace
					c3 = 0
					driveutils.createNewLog(tmppath3+".ext.tmp",True)
					writelog = open(tmppath3+".ext.tmp", 'ab')
					with open(tmppath3, 'rb') as f2:
					    for rline2 in f2.readlines():
#							print '   ', c3,best_fit['count'],'  '
#							print '      ',rline2.rstrip()
#							print '      ',best_fit['line'].rstrip()
							if rline2.rstrip() == best_fit['line'].rstrip():
#								print '       - skip writing: ',rline2.rstrip()
								continue
							writelog.write( rline2.rstrip()+"\n" )
							c3+=1
					writelog.close()
					if os.path.exists(tmppath3+".ext.tmp"):
						if os.path.exists(tmppath3+".ext"):
							os.remove(tmppath3+".ext")
						os.rename(tmppath3+".ext.tmp",tmppath3+".ext")

					c+=1
		movedlog.close()

		if os.path.exists(tmppath3+".ext"):
			driveutils.sortLogByPath(tmppath3+".ext")


def searchForMove(readname,runname,logsetname,tmpfolder,compSET,masterlist,datasets,useopts=None):

	timestamp = masterlist['_newmaster']['newtime']
	tmppath = tmpfolder+'/md5vali/'+readname+'/'+runname+'/'+timestamp+'/miss-search/';

	for sourcename in compSET['_sources'].keys():
		compobj = compSET['_sources'][sourcename]

		movedpath = tmppath+ 'moved/'+logsetname+'/moved-'+logsetname+'-'+sourcename+'-'+timestamp+'.txt'

		compState = compSET['_sources'][sourcename]['state']
		# is a non-master source in a new location?
		if compState == 'missing' or compState == 'new':
			found_item = None
			if os.path.exists(movedpath):
				with open(movedpath, 'rb') as f2:
				    for rline2 in f2.readlines():

						inrunname = re.findall('^([^,]*),\s*',rline2)[0]
						inlogsetname = re.findall('^(?:[^,]*,\s*){1}([^,]*),',rline2)[0]
						insourcename = re.findall('^(?:[^,]*,\s*){2}([^,]*),\s*',rline2)[0]
						insha = re.findall('^(?:[^,]*,\s*){3}\s*([^,]*),',rline2)[0]
						inbsize = re.findall('^(?:[^,]*,\s*){4}\s*([^,]*),',rline2)[0]
						inmtype = re.findall('^(?:[^,]*,\s*){5}\s*([^,]*),',rline2)[0]
						inobjstr = re.findall('^(?:[^,]*,\s*){6}(\{.*\})\s*$',rline2)[0]
						inobj = json.loads(inobjstr)

						# if this has a cur path (ie a 'new' source), use it.  otherwise, grab from summary
						if compSET['_sources'][sourcename]['cur_path'] is not None:
							pathComp = '/'+ compSET['_sources'][sourcename]['cur_path'].lstrip('/')
						else:
							pathComp = compSET['_summary']['path']
						pathFrom = '/'+ inobj['from'].lstrip('/').encode('utf-8')
						pathTo = '/'+ inobj['to'].lstrip('/').encode('utf-8')

						# skip if attempting to match a 'move' record not from the same group
						if runname != inrunname or logsetname != inlogsetname or sourcename != insourcename:
							continue

						# if the current source is missing, but both the built-path and oldmaster path don't match the 'move' record
						if compState == 'missing' and pathFrom != pathComp and pathFrom != compSET['_oldmaster']['cur_path']:
							continue
						# if the current source is new, but the built-path don't match the 'move' record
						if compState == 'new' and pathTo != pathComp:
							continue


						oldmtype='md5'
						if 'cur_mtype' in compSET['_oldmaster'].keys():
							oldmtype=compSET['_oldmaster']['cur_mtype']

						# filter out conditions where the hashes do not match for 'missing' and then 'new'

						if compState == 'missing' and insha != compSET['_sources'][sourcename]['cur_sha'] and insha != compSET['_oldmaster']['cur_sha']:
							# If this file is missing, and:
							#		movedfile.sha != currentfile.sha and movedfile.sha != oldmaster.sha,
							if inmtype == oldmtype:
								continue
							elif inbsize != compSET['_oldmaster']['cur_bsize']:
								continue
							else:
								#	verify the currentfile is not the movedfile by calculating matching mtype shas
								sourcehashes=None
								inhashes=inobj['hashes']

								if 'hashes' in compSET['_sources'][sourcename].keys():
									sourcehashes=compSET['_sources'][sourcename]['hashes']
								else:
									# Fetch old type hash of new object
									mcount = None
									if 'useblocks' in useopts.keys() and '_count' in useopts['useblocks'].keys():
										mcount = int(useopts['useblocks']['_count'])
									basepath=comparefns.grabBasePath(logsetname,sourcename,datasets)
									thepath=basepath.rstrip('/')+"/"+compSET['_sources'][sourcename]['cur_path']
									if os.path.isfile(thepath):
										sourcehashes={}
										if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
											print 'getsha - movecheck1,',pathComp,pathTo,pathFrom,sourcename,inhashes,compState
											print '        -  and',insha, compSET['_sources'][sourcename]['cur_sha'],compSET['_sources'][sourcename],oldmtype,'!=',useopts['mtype'],thepath
										sourcehashes[oldmtype]=driveutils.shaSum(thepath,mcount,oldmtype)
										if 'mtype' in useopts.keys() and oldmtype != useopts['mtype']:
											if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
												print '    - movecheck2,',useopts['mtype'],compSET['_sources'][sourcename]['cur_path']
											sourcehashes[useopts['mtype']]=driveutils.shaSum(thepath,mcount,useopts['mtype'])

								if sourcehashes is not None:
									if oldmtype in sourcehashes.keys() and oldmtype in inhashes.keys():
										if inhashes[oldmtype] != sourcehashes[oldmtype]:
											if sourcehashes[oldmtype] != compSET['_oldmaster']['cur_sha']:
												continue
									else:
										totalmtypes=[]
										totalmtypes.extend( sourcehashes.keys() )
										totalmtypes.extend( inhashes.keys() )
										mysettypes = set(totalmtypes)
										mysetarray = list(mysettypes)
										hashc=0
										badtrip=False
										if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
											print "~~~#1#~~",oldmtype,pathComp,compSET['_oldmaster']
										for hash in mysetarray:
											if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
												print "~~~#2#~~",hash,sourcehashes,inhashes,',',compSET['_oldmaster']['cur_sha']
											if hash in sourcehashes.keys() and hash in inhashes.keys():
												if inhashes[hash] != sourcehashes[hash]:
													badtrip=True
													break
												hashc=hashc+1
										if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
											print "~~~#3#~~",hash,badtrip,hashc
										if badtrip or hashc == 0:
											continue
										sys.exit(1)


								if sourcehashes is None:
									print "FFFFFFFFFFFFFFFFFFFFFFFUUUUUUUUUUUUUUUUUUUUUUUCCCCCCCCCCCK THIS"
									print compState, sourcename, inmtype, insha, oldmtype
									print '.source.', oldmtype, sourcehashes
									print '.in.', oldmtype, inhashes
									print '   in:',rline2
									print '   inobj:',inobj
									print '------'
									print '.old.',compSET['_oldmaster']
									print '.source.',compSET['_sources'][sourcename]
									sys.exit(1)

						if compState == 'new' and insha != compSET['_sources'][sourcename]['cur_sha']:
							if inmtype == compSET['_sources'][sourcename]['cur_mtype']:
								continue
							elif inbsize != compSET['_sources'][sourcename]['cur_bsize']:
								continue
							else:
								#	verify the currentfile is not the movedfile by calculating matching mtype shas
								sourcehashes=None
								inhashes=inobj['hashes']

								if 'hashes' in compSET['_sources'][sourcename].keys():
									sourcehashes=compSET['_sources'][sourcename]['hashes']
								else:
									# Fetch old type hash of new object
									mcount = None
									if 'useblocks' in useopts.keys() and '_count' in useopts['useblocks'].keys():
										mcount = int(useopts['useblocks']['_count'])
									basepath=comparefns.grabBasePath(logsetname,sourcename,datasets)
									thepath=basepath.rstrip('/')+"/"+compSET['_sources'][sourcename]['cur_path']
									if os.path.isfile(thepath):
										matched = False
										sourcehashes={}
										if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
											print '~~d~', inobj,compSET['_sources'][sourcename]['cur_path']
										if inobj['to'] == compSET['_sources'][sourcename]['cur_path']:
											curmtype = compSET['_sources'][sourcename]['cur_mtype']
											if curmtype in inobj['hashes'].keys():
												if inobj['hashes'][curmtype] == compSET['_sources'][sourcename]['cur_sha']:
													matched = True
													sourcehashes[curmtype] = compSET['_sources'][sourcename]['cur_sha']

										if not matched:
											if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
												print 'getsha2 - movecheck3,',pathComp,pathTo,pathFrom,sourcename,inhashes,compState
												print '        -  and',insha, compSET['_sources'][sourcename]['cur_sha'],compSET['_sources'][sourcename],oldmtype,'!=',useopts['mtype'],thepath
											if oldmtype not in sourcehashes.keys():
												sourcehashes[oldmtype]=driveutils.shaSum(thepath,mcount,oldmtype)
											if 'mtype' in useopts.keys() and oldmtype != useopts['mtype']:
												if useopts['mtype'] not in sourcehashes.keys():
													if 'verbose' in useopts.keys() and useopts['verbose'] >= 1:
														print '    - movecheck4,',useopts['mtype'],compSET['_sources'][sourcename]['cur_path']
													sourcehashes[useopts['mtype']]=driveutils.shaSum(thepath,mcount,useopts['mtype'])

								if sourcehashes is not None:
									if oldmtype in sourcehashes.keys() and oldmtype in inhashes.keys():
										if inhashes[oldmtype] != sourcehashes[oldmtype]:
											continue
									else:
										totalmtypes=[]
										totalmtypes.extend( sourcehashes.keys() )
										totalmtypes.extend( inhashes.keys() )
										mysettypes = set(totalmtypes)
										mysetarray = list(mysettypes)
										hashc=0
										badtrip=False
										for hash in mysetarray:
											if hash in sourcehashes.keys() and hash in inhashes.keys():
												if inhashes[hash] != sourcehashes[hash]:
													badtrip=True
													break
												hashc=hashc+1
										if badtrip or hashc == 0:
											continue

								if sourcehashes is None:
									print "FFFFFFFFFFFFFFFFFFFFFFFUUUUUUUUUUUUUUUUUUUUUUUCCCCCCCCCCCK THIS 2"
									print compState, sourcename, inmtype, insha, oldmtype
									print '.source.', oldmtype, sourcehashes
									print '.in.', oldmtype, inhashes
									print '   in:',rline2
									print '   inobj:',inobj
									print '------'
									print '.old.',compSET['_oldmaster']
									print '.source.',compSET['_sources'][sourcename]
									sys.exit(1)


#						print '*3a',compState,' and '
#						print '*3b',pathFrom,'==',
#						print '*3c',pathComp,'==',
#						print '*3d',pathTo,' and ',
#						print '*3e',compSET['_oldmaster']['cur_path']

#						print '*3',compState,' and ',pathFrom,'==',pathComp,'==',pathTo,' and ',compSET['_oldmaster']['cur_path']


						found_item = {'runname':inrunname,'logsetname':inlogsetname,'sourcename':insourcename,'state':compState,'sha':insha,'mtype':inmtype,'obj':inobj,'hashes':inobj['hashes']}
						break
				f2.close()
				if found_item is not None:
#					print '** 7',found_item['state'],found_item
					if found_item['state'] == 'missing':
						compSET['_sources'][sourcename]['state'] = 'moved'
						compSET['_sources'][sourcename]['moved_to'] = found_item['obj']['to']
						compSET['_sources'][sourcename]['moved_from'] = found_item['obj']['from']


					if found_item['state'] == 'new':
						compSET['_sources'][sourcename]['state'] = 'moved_away'




#					SET UP TEST LOGS FOR 'NO ASK','LAST-ASK','LAST-DROP','DROP',MOVE-FILE vs CONFLICT vs RENAME
#					TEST ABOVE SCENARIOS

# build movelog:
#	search for run,set,source,md5 match
#	find best fit:
#		same folder: lowest changed characters
#		diff folder: *************
#   save best fit "runname,logsetname,sourcename,md5,{from:_,to:_}"
#   delete used entries from both logs
# uniquify sort
#
# compare stage:
#	if new && in log && oldmaster.state == missing && path == "to:"
#		skip?
#	if missing && in log && oldmaster.state == present && path == "from:"
#		create moved master line
#		print "moved from" for source
#		print "moved to" for source

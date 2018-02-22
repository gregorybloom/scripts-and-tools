
	def	resolveViaLogs(compset,steplist,newlog,logitem,matchnames,runname,logsetname,datasets,useopts=None):
		if useopts is None:
			useopts={}

		fullpath = re.findall(r'(\/\/.*)$',logitem['line'])[0]
		startline = re.findall(r'^(\w+,\s*\d+,[^,]+,\s*)\/',logitem['line'])[0]
		masterline = startline+"/masterpath/"+logsetname+fullpath+"\n"
#
		# ADD TO MISSING LOG
		if compset['ptype'] == "sXdXmP":
			if '_holddata' not in useopts.keys():
				useopts['_holddata']={}

			print
			logpath=masterlist['_newmaster']['altpath']+'/md5vali-missing-'+masterlist['_newmaster']['alttime']+'.txt'
			driveutils.createNewLog(logpath,True)
			driveutils.addToLog( masterline, logpath )

			obj={}
			for lname in datasets['logset'][runname][logsetname].keys():
				obj[lname]='missing'
			addToTotalCount(useopts['_holddata'],runname,logsetname,obj)

		val = actOnUseOpts('add',useopts,masterlist,runname,logsetname,{'logitem':logitem,'compset':compset})
		print "#1 ",val,logitem,compset
		if val == 'exit':
			return

		action=''

		if compset['ptype'] == "sPdPmP":
			if compset['stype'] == "sSdS'mS" or compset['stype'] == "sS'dSmS":
				action="conflict"
			if compset['stype'] == "sSdS'mS'" or compset['stype'] == "sS'dSmS'":
				action="conflict"
		elif compset['ptype'] == "sPdPmX":
			if re.match("^sSdS",compset['stype']):
				action="new"
			if re.match("^sS'dS",compset['stype']) or re.match("^sSdS'",compset['stype']):
				action="new conflict"
		elif compset['ptype'] == "sPdXmP" or compset['ptype'] == "sXdPmP":
			if re.match(".*[ds]S'.*",compset['stype']):
				action="conflict one missing"
			else:
				action="one missing"
		elif compset['ptype'] == "sPdXmX" or compset['ptype'] == "sXdPmX":
			action="new one missing"

		overall = None
		if action=="":
			if '_holddata' not in useopts.keys():
				useopts['_holddata']={}

			obj={}
			for lname in datasets['logset'][runname][logsetname].keys():
				obj[lname]='present'
			addToTotalCount(useopts['_holddata'],runname,logsetname,obj)
		else:
			obj={}
			for logn in steplist.keys():
				print 'b  ',compset['ptype'], logn, matchnames, compset['path'], steplist[logn]['cur_path']
				if compset['path'] == steplist[logn]['cur_path']:
					if logn in matchnames:
						if re.match("^sEdEm",compset['stype']):
							obj[logn]='error'
						elif re.match(".*mX.*",compset['ptype']):
							obj[logn]='new'
						else:
							obj[logn]='present'
					elif re.match("^sEdEm",compset['stype']):
						obj[logn]='error'
					else:
						obj[logn]='conflict'
				elif re.match("^sEdEm",compset['stype']):
					obj[logn]='error'
				else:
					obj[logn]='missing'
#				print '    ..',logn,obj[logn]

			if '_holddata' not in useopts.keys():
				useopts['_holddata']={}
			overall=addToTotalCount(useopts['_holddata'],runname,logsetname,obj)

			logpath=masterlist['_newmaster']['altpath']+'/md5vali-'+overall+'-'+masterlist['_newmaster']['alttime']+'.txt'
			driveutils.createNewLog(logpath,True)

			driveutils.addToLog( "\n-------- md5 "+overall+" --------\n", logpath )
			print
			print "-------- md5 "+overall+" --------"
			if re.match(".*mX.*",compset['ptype']):
				print "master - missing, "+"/masterpath/"+logsetname+fullpath
#				driveutils.addToLog( "master - missing, "+masterline, logpath )
				driveutils.addToLog( "master - missing, "+"/masterpath/"+logsetname+fullpath+"\n", logpath )
			else:
				print "master - "+masterline.rstrip()
				driveutils.addToLog( "master - "+masterline, logpath )
			for logn in steplist.keys():
				if compset['path'] == steplist[logn]['cur_path']:
					if logn in matchnames:
						print logn,"- match, "+steplist[logn]['line'].rstrip()
						driveutils.addToLog( logn+"- match, "+steplist[logn]['line'], logpath )
					else:
						print logn,"- conflict, "+steplist[logn]['line'].rstrip()
						driveutils.addToLog( logn+"- conflict, "+steplist[logn]['line'], logpath )
				else:
#					print '**',runname,logsetname,logn,datasets['found'].keys(),datasets['targets'].keys()
					pathA = datasets['found'][logn]
					pathB = datasets['targets'][logsetname][logn]
					print logn,"- missing, "+pathA+pathB+'/'+compset['path']
					driveutils.addToLog( logn+"- missing, "+pathA+pathB+'/'+compset['path']+'\n', logpath )
			print "------------------------------"
			driveutils.addToLog( "------------------------------\n", logpath )
		print

		## ADD TO MASTER PATH
		if overall != "conflict" and overall != "error":
			print "==== ",masterline
			newlog['obj'].write(masterline)

	def	resolveViaError(compset,steplist,masterlist,newlog,logitem,matchnames,runname,logsetname,datasets,useopts=None):
		if '_holddata' not in useopts.keys():
			useopts['_holddata']={}

#		print compset,steplist.keys(),masterlist['_oldmaster'].keys(),steplist,'  @@@@  ',newlog,'  @@@@  ',logitem,matchnames,runname
		if(masterlist['_oldmaster']['line'] == ''):
			fullpath = '/'+compset['path']
			startline = "**********, **********, **********, "
		elif not re.match(".*mX.*",compset['ptype']):
			fullpath = re.findall(r'(\/\/.*)$',masterlist['_oldmaster']['line'])[0]
			startline = re.findall(r'^(\w+,\s*\d+,[^,]+,\s*)\/',masterlist['_oldmaster']['line'])[0]
		else:
			fullpath = '/'+compset['path']
			startline = "**********, **********, **********, "

		masterline = startline+"/masterpath/"+logsetname+fullpath+"\n"

		obj={}
		for logn in steplist.keys():
#			print 'E   ',compset['ptype'], logn, matchnames, compset['path'], steplist[logn]
			if 'loadErr' in steplist[logn].keys() and steplist[logn]['loadErr']:
				obj[logn]='error'
			elif compset['path'] == steplist[logn]['cur_path']:
				if logn in matchnames:
					if re.match(".*mX.*",compset['ptype']):
						obj[logn]='new'
					else:
						obj[logn]='present'
				else:
					obj[logn]='conflict'
			else:
				obj[logn]='missing'

		overall=addToTotalCount(useopts['_holddata'],runname,logsetname,obj)

		logpath=masterlist['_newmaster']['altpath']+'/md5vali-'+overall+'-'+masterlist['_newmaster']['alttime']+'.txt'
		driveutils.createNewLog(logpath,True)

		driveutils.addToLog( "\n-------- md5 "+overall+" --------\n", logpath )
		print
		print "-------- md5 "+overall+" --------"
		if re.match(".*mX.*",compset['ptype']):
			print "master - missing, "+"/masterpath/"+logsetname+fullpath
#			driveutils.addToLog( "master - missing, "+masterline, logpath )
			driveutils.addToLog( "master - missing, "+"/masterpath/"+logsetname+fullpath+"\n", logpath )
		else:
			print "master - "+masterline.rstrip()
			driveutils.addToLog( "master - "+masterline, logpath )
		for logn in steplist.keys():
			if compset['path'] == steplist[logn]['cur_path']:
				if 'loadErr' in steplist[logn].keys() and steplist[logn]['loadErr']:
					print logn,"- error, "+steplist[logn]['line'].rstrip()
					driveutils.addToLog( logn+"- error, "+steplist[logn]['line'], logpath )
				elif logn in matchnames:
					print logn,"- match, "+steplist[logn]['line'].rstrip()
					driveutils.addToLog( logn+"- match, "+steplist[logn]['line'], logpath )
				else:
					print logn,"- conflict, "+steplist[logn]['line'].rstrip()
					driveutils.addToLog( logn+"- conflict, "+steplist[logn]['line'], logpath )
			else:
#					print '**',runname,logsetname,logn,datasets['found'].keys(),datasets['targets'].keys()
				pathA = datasets['found'][logn]
				pathB = datasets['targets'][logsetname][logn]
				print logn,"- missing, "+pathA+pathB+'/'+compset['path']
				driveutils.addToLog( logn+"- missing, "+pathA+pathB+'/'+compset['path']+'\n', logpath )
		print "------------------------------"
		driveutils.addToLog( "------------------------------\n", logpath )
		print

		## ADD TO MASTER PATH
		if re.match(r'^(\w+,\s*\d+,[^,]+,\s*)',masterline):
			print "==== ",masterline
			newlog['obj'].write(masterline)

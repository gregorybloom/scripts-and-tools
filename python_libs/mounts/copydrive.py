
import os, sys, hashlib, time, shutil, re

from maintenance_loader import *



logfolder = "logs"

ix = 0
gc = 0

def beginCopyDrive(base, target, logname, copyopts, walknotes, reuse=False):
	global gc
	gc=0

	if( not os.path.exists(base) or not os.path.isdir(base) ):
		print ' FAILURE: '+base+' does not exist!'
		return
	if( not os.path.exists(target) or not os.path.isdir(target) ):
		if not os.path.exists(target):
			try:
				os.makedirs(target)
			except OSError as exception:
	#			if exception.errno != errno.EEXIST:
				raise
		else:
			print ' FAILURE: '+target+' does not exist!'
			return

	if logname is not None:
		driveutils.createNewLog(logname,reuse)

	walkDrives(base, target, '', logname, walknotes)

def beginResolveErrs(base, target, logname, copyopts, walknotes, reuse=False):
	print
	print
	for groupname,groupset in walknotes.iteritems():
		for classname,classdata in groupset.iteritems():
			for classitem in classdata:
				printline = ''.join(('-(1) ',groupname,' ',classname,' = ', str(classitem['notes']), '**', str(classitem['data'])))
#				print printline
#				driveutils.addToLog(printline+'\n', logname)

	if 'runerrs' in walknotes.keys():
		tempcount=0
		while 'walktree' in walknotes['runerrs'].keys():

			walklist = []
			walklist.extend(walknotes['runerrs']['walktree'])

			walknotes['runerrs']['walktree'] = None
			del walknotes['runerrs']['walktree']

#			print tempcount, walknotes['runerrs'].keys()
			for classitem in walklist:
				taskobj=classitem['data']
				taskobj['action']='walktree'
				notesobj={'errs':{}}
				notesobj['errs']['OSError'] = classitem['notes']['val']

				printline= ''.join(('* Reattempt','walktree',' = ', str(taskobj), '**', str(notesobj)))
#				print printline
#				driveutils.addToLog(printline+'\n', logname)

				walkDrives('', taskobj['pathTo'].rstrip('/'), '', logname, walknotes)

			if 'walktree' in walknotes['runerrs'].keys() and len(walknotes['runerrs']['walktree']) > 0:
				print '-------------'
				for classitem in walknotes['runerrs']['walktree']:
					print 'walktree',':  ',classitem['data']['pathFrom']
				print '-------------'

				if 'force_no' in copyopts.keys():
					break
				leaveq = raw_input(("Reattempt above copies?\n"))
				if not re.search('^(?:Y|y|YES|Yes|yes)\s*$',leaveq):
					break

#			time.sleep(3)
			tempcount+=1
			print


	fails=['remove','deltree','makedirs','copyfile']
	if 'runerrs' in walknotes.keys():
		for f in fails:
#			if f in walknotes['runerrs'].keys():
			while f in walknotes['runerrs'].keys():
				walklist = []
				walklist.extend(walknotes['runerrs'][f])
				walknotes['runerrs'][f] = None
				del walknotes['runerrs'][f]

				for classitem in walklist:
					taskobj=classitem['data']
					taskobj['action']=f
					notesobj={'errs':{}}

					letterval = classitem['notes']['val']
#					if letterval != 'A' and letterval != 'B':
#						print ' === ',letterval,f,taskobj,classitem

					errtype = classitem['notes']['type']
					if errtype == 'OSError' or errtype == 'IOError':
						notesobj['errs'][ errtype ]=letterval
					if letterval != 'A' and letterval != 'B':
						if classitem['notes']['type'] == 'OSError':
							notesobj['errs']['IOError'] = chr(ord(letterval) + 1)
						if classitem['notes']['type'] == 'IOError':
							notesobj['errs']['OSError'] = chr(ord(letterval) - 1)
					printline= ''.join(('=(3)* reattempt ',f,' = ', str(taskobj), '**', str(notesobj)))
#					print printline
#					driveutils.addToLog(printline+'\n', logname)
					performTask(taskobj,notesobj, logname, walknotes)


				if f in walknotes['runerrs'].keys() and len(walknotes['runerrs'][f]) > 0:
					print '-------------'
					for classitem in walknotes['runerrs'][f]:
						print classitem['data']['action'],':  ',classitem['data']['pathTo']
					print '-------------'
					if 'force_no' in copyopts.keys():
						break
					leaveq = raw_input(("Reattempt failed tasks?\n"))
					if not re.search('^(?:Y|y|YES|Yes|yes)\s*$',leaveq):
						break

	for groupname,groupset in walknotes.iteritems():
		for classname,classdata in groupset.iteritems():
			for classitem in classdata:
				printline = ''.join(('*ERR* ',classname,' = ', str(classitem['notes']), '**', str(classitem['data'])))
				print printline
				driveutils.addToLog(printline+'\n', logname+'.ERR.log')

#walknotes[group][grclass]=[]
#noteset['data']=data
#noteset['notes']=notes
#walknotes[group][grclass].append(noteset)
# addWalkNotes(walknotes,'runerrs','deltree',{'pathto':pathTo},{'type':'OSError','val':'C','err':str(exception)})

def addWalkNotes(walknotes, group, grclass, data, notes):
	if group not in walknotes.keys():
		walknotes[group]={}
	if grclass not in walknotes[group].keys():
		walknotes[group][grclass]=[]
	noteset={}
	noteset['data']=data
	noteset['notes']=notes
	walknotes[group][grclass].append(noteset)

def performTask(task, opts, logname, walknotes):
	pathTo = task['pathTo']
	logline = None
	errline = None
	if task['action'] == "walktree":
		return 0
	if task['action'] == "remove":
		logline = '- '+ pathTo
		errline = 'failed to remove file: ' +pathTo
	if task['action'] == "deltree":
		logline = 'deleting tree: ' +pathTo
		errline = 'failed to remove tree: ' +pathTo
	if task['action'] == "copyfile":
		logline = '  % ' +pathTo
		if opts['errs']['OSError'] == 'G':
			logline = '  + '+ pathTo
		errline = 'failed to copy file: ' +pathTo
	if task['action'] == "makedirs":
		logline = '  + '+ pathTo
		errline = 'failed to make directory: ' +pathTo

	try:
		print logline+'\n'
		if logname is not None and logline is not None:
			driveutils.addToLog(logline+'\n', logname)
		if task['action'] == "remove":
			os.remove(pathTo)
		if task['action'] == "deltree":
			shutil.rmtree(pathTo)
		if task['action'] == "copyfile":
#			print '*D',task,opts['errs']
			shutil.copyfile(task['pathFrom'],pathTo)
		if task['action'] == "makedirs":
			os.makedirs( pathTo )
		return 1
	except OSError as exception:
		letval = opts['errs']['OSError']
		print '*'+letval+'* err on '+str(exception)
		objdata = {'pathTo':pathTo}
		addWalkNotes(walknotes,'runerrs',task['action'],task,{'type':'OSError','val':letval,'err':str(exception)})
	except IOError as exception:
		letval = opts['errs']['IOError']
		print '*'+letval+'* err on '+str(exception)
		objdata = {'pathTo':pathTo}
		addWalkNotes(walknotes,'runerrs',task['action'],task,{'type':'IOError','val':letval,'err':str(exception)})

	if logname is not None:
		driveutils.logCriticalError(errline, logname)
		driveutils.logCriticalError(str(exception), logname)
		driveutils.addToLog(errline+'\n', logname)
		driveutils.addToLog('** err on '+str(exception)+'\n', logname)
	return 0





def walkDrives(base, target, path, logname, walknotes):

# addWalkNotes(walknotes,'runerrs','deltree',{'pathto':pathTo},{'type':'OSError','val':'C','err':str(exception)})

	global ix
	global gc

#	print base, os.path.islink(base)
#	print base+"/"+path, os.path.islink(base+"/"+path)
#	return
	if os.path.islink(base+"/"+path):
		return
	if os.path.islink(target+"/"+path):
		return
	try:
		files = driveutils.readDir(base+"/"+path, logname)
		files2 = driveutils.readDir(target+"/"+path, logname)
	except OSError as exception:
		addWalkNotes(walknotes,'runerrs','walktree',{'pathFrom':base+"/"+path,'pathTo':target+"/"+path},{'type':'OSError','val':'K','err':str(exception)})
		return

#	print ' , ', base+'/'+path
#	print files
#	return

	print ' v '+target+'/'+path

	for file2 in files2:
		namestr = str(file2)

		pathFrom = base+"/"+path+namestr
		pathTo = target+"/"+path+namestr

		if (driveutils.ignoreFile(namestr,path,pathTo)):
			continue


		if(  not os.path.exists(pathFrom) and os.path.exists(pathTo)  ):

			if( not os.path.isdir(pathTo) ):
				performTask({'action':'remove','pathTo':pathTo}, {'errs':{'OSError':'A'}}, logname, walknotes)

			else:
				performTask({'action':'deltree','pathTo':pathTo}, {'errs':{'OSError':'B'}}, logname, walknotes)



	for filename in files:
		namestr = str(filename)

		pathFrom = base+"/"+path+namestr
		pathTo = target+"/"+path+namestr

		if (driveutils.ignoreFile(namestr,path,pathFrom)):
			continue


		if(  not os.path.isdir(pathFrom) and os.path.exists(pathTo)  ):

			if( not os.path.isdir(pathTo) ):
				objA = driveutils.getFileInfo( pathFrom )
				objB = driveutils.getFileInfo( pathTo )

				test1 = ( objA['filename'] == objB['filename'] )
				test2 = ( objA['sha'] == objB['sha'] )
				test3 = ( objA['bytesize'] == objB['bytesize'] )
			else:
				test1 = False
				test2 = False
				test3 = False
				performTask({'action':'deltree','pathTo':pathTo}, {'errs':{'OSError':'C','IOError':'D'}}, logname, walknotes)

			if(test1 and test2 and test3):
				continue
			else:
				success = performTask({'action':'copyfile','pathTo':pathTo,'pathFrom':pathFrom}, {'errs':{'OSError':'E','IOError':'F'}}, logname, walknotes)
				if success == 0:
					continue

		elif(  not os.path.isdir(pathFrom) and not os.path.exists(pathTo)  ):
			success = performTask({'action':'copyfile','pathTo':pathTo,'pathFrom':pathFrom}, {'errs':{'OSError':'G','IOError':'H'}}, logname, walknotes)
			if success == 0:
				continue

		elif(  os.path.isdir(pathFrom)  ):

			if(  not os.path.exists(pathTo)  ):
				performTask({'action':'makedirs','pathTo':pathTo}, {'errs':{'OSError':'I','IOError':'J'}}, logname, walknotes)

#			print '**', base, target, path+namestr+"/", logname, walknotes
			walkDrives(base, target, path+namestr+"/", logname, walknotes)

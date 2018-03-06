
from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv
from sys import version_info



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

	if '_holddata' not in useopts.keys():
		useopts['_holddata']={}


	##  If the stage is 'add', set aside any missing values from "master" into 'dropold' or 'askold' in '_holddata'
	if stage == "add":
		if 'dropold' in useopts.keys() or 'askdropold' in useopts.keys():
			if compSET['_summary']['masterstate'] != "missing":
				statelist=compSET['_summary']['groupstates'].keys()
				if len(statelist)==1 and "missing" in statelist:
					missinglogpath=masterlist['_newmaster']['newpath']+'/missing-quicklists/missing-'+logsetname+'-'+masterlist['_newmaster']['newtime']+'.txt'

					driveutils.createNewLog(missinglogpath,False)

					reline = compSET['_summary']['masterline']
#					reline = re.findall("^(?:[^,]+,){3}[^\/]*(\/.*\S)\s*$",reline)[0]
					driveutils.addToLog( reline.rstrip()+"\n", missinglogpath )


					if 'dropoldlogs' not in useopts['_holddata'].keys():
						useopts['_holddata']['dropoldlogs']=[]
					if missinglogpath not in useopts['_holddata']['dropoldlogs']:
						if 'askdropold' in useopts.keys():
							useopts['_holddata']['dropoldlogs'].append({'runname':runname,'logsetname':logsetname,'path':missinglogpath,'ask':True})
						else:
							useopts['_holddata']['dropoldlogs'].append({'runname':runname,'logsetname':logsetname,'path':missinglogpath})

					return 'exit'

	if stage == 'end':
		if 'askdropold' in useopts.keys():
			if '_holddata' in useopts.keys():
				if 'dropoldlogs' in useopts['_holddata'].keys():
					heldlist=[]
					for obj in useopts['_holddata']['dropoldlogs']:
						if obj['runname']==runname and obj['logsetname']==logsetname and obj['ask']==True:
							heldlist.append(obj)

					if len(heldlist)==0:
						return
					print
					print
					for obj in heldlist:
						filepath=obj['path']
						with open(filepath) as thefile:
						    for rline in thefile.readlines():

								reline = rline
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
					########################################################  WORKING FROM HERE -- ######################################
					# look at 'dropold' condition below.  Track down what this results in and why?
					if re.match("^\s*([Yy](?:[Ee][Ss])?)\s*$",conf):
						print "Removed."
						for obj in useopts['_holddata']['dropoldlogs']:
							if obj['runname']==runname and obj['logsetname']==logsetname and 'ask' in obj.keys() and obj['ask']==True:
								del obj['ask']
#						if 'dropold' not in useopts['_holddata'].keys():
#							useopts['_holddata']['dropold']=[]
#						useopts['_holddata']['dropold'].extend(heldlist)

					else:
						newlog=masterlist['_newmaster']
						for obj in heldlist:
							filepath=obj['path']
							with open(filepath) as thefile:
							    for rline in thefile.readlines():

#							fullpath = re.findall(r'(\/\/.*)$',obj['line'])[0]
#							startline = re.findall(r'^(\w+,\s*\d+,[^,]+,\s*)\/',obj['line'])[0]
#							masterline = startline+"/masterpath/"+logsetname+fullpath+"\n"

									newlog['obj'].write(rline+"\n")
						print "Canceling removal."

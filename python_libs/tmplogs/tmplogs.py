from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv

def clearTmpMD5Logs(logtype,groupname,logfolder):
	logpath = logfolder+'/'+logtype+'/'+groupname+'/';

	temps=['pieces','parts','sections']
	for tempfolder in temps:
		if os.path.exists(logpath+tempfolder+'/'):
			try:
				shutil.rmtree(logpath+tempfolder+'/')
			except OSError as exception:
				print '*A* err on '+tempfolder+', '+str(exception)
				raise exception

def createNewTmpMD5Logs(logtype,groupname,timestr,foldersets,foundlist,logfolder,md5opts=None):
	if md5opts is None:
		md5opts={}
	if 'walkopts' not in md5opts.keys():
		md5opts['walkopts']={}

	logset={}
	mastset={}
	errset={}
	loglist=[]

	if groupname not in logset.keys():
		logset[groupname]={}

	logpath = logfolder+'/'+logtype+'/'+groupname+'/';

	for setname,folderset in foldersets.iteritems():
		for sourcename,folderpath in folderset.iteritems():

			if setname not in logset[groupname].keys():
				logset[groupname][setname]={}
			if sourcename not in foundlist.keys():
				continue

			logname= logpath+'pieces/'+sourcename+'/'+setname+'/'+logtype+'-'+sourcename+'-'+timestr+'.txt'
			driveutils.createNewLog(logname,False)

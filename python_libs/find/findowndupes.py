
import os, sys, hashlib, time, re
from maintenance_loader import *



logfolder = "logs"

hashes = {}
gd=0


def findOwnDupes(log, logname):
	driveutils.createNewLog(logfolder+'/'+ logname)
	beginWalkCompare(log, logname)

def beginWalkCompare(log, logname):
	global hashes
	global gd

	hashes = {}
	gd=0

	logAf = open(log, 'rb')
	while 1:
		line = logAf.readline()
		if not line:
			break

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if re.search(reg,line):
			objA = driveutils.decomposeFileLog(line)

			if hashes.has_key(objA['sha']):
				print '/x ' + objA['fulltext'].strip()
				continue

			if (gd%10)==0:
				print '/ ' + objA['fulltext'].strip()


			hashes[objA['sha']] = 0

			if not preWalkCompare(objA, log):
				continue

			hashes[objA['sha']] = 1
#			logname = buildLogName(logname,log)

			count = walkCompare(objA, log, logname)

def buildLogName(logname,otherlog):
	div = logname.find('/')
	if div >= 0:
		parts = logname.rsplit('/',2)
		path = parts[0]
	else:
		path=""
	div = otherlog.find('/')
	if div >= 0:
		parts = logname.rsplit('/',2)
		logname = parts[1]

	logname = path +'/'+ logname
	return logname

def preWalkCompare(objA, logB):
	global hashes

	logB2f = open(logB, 'rb')
	while 1:
		line2 = logB2f.readline()
		if not line2:
			break

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if re.search(reg,line2):
			objB2 = driveutils.decomposeFileLog(line2)

			if (objA['sha'] == objB2['sha']):
				if(objA['fullpath'] != objB2['fullpath']):
					return True
	return False


def walkCompare(objA, logB, logname):
	global hashes
	global gd

	c=0
	logBf = open(logB, 'rb')
	while 1:
		line2 = logBf.readline()
		if not line2:
			break

		reg = r'^[A-Za-z0-9]+, [0-9]+,'
		if re.search(reg,line2):
			objB = driveutils.decomposeFileLog(line2)

			if (objA['sha'] == objB['sha']):

				if(objA['fullpath'] == objB['fullpath']):
					driveutils.addToLog("// "+objB['fulltext'], logfolder+'/'+ logname)
					if (gd%10)==0:
						print '- ' + objB['fulltext'].strip()
				else:
					driveutils.addToLog(objB['fulltext'], logfolder+'/'+ logname)
					if (gd%10)==0:
						print '* ' + objB['fulltext'].strip()

				c=c+1
				gd=gd+1
	return c


def compareFiles(objA, objB):

	if objA['sha'] != objB['sha']:
		return False
	if objA['bytesize'] != objB['bytesize']:
		return False
	return True

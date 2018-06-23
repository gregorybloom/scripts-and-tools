from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv, datetime


def findDupesBetweenLogs(md5log, md5log2, resultlog, tmpfolder, runopts):

	driveutils.sortLogByPath(md5log,0)
	driveutils.sortLogByPath(md5log2,0)

	driveutils.createNewLog(resultlog,False)
	dupelog = open(resultlog, 'ab')

	md5searchlog = {}
	md5searchlog['obj'] = open(md5log, 'r')
	md5searchlog['line'] = md5searchlog['obj'].readline()
	md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'])
	md5searchlog['last'] = None

	md5searchlog2 = {}
	md5searchlog2['obj'] = open(md5log2, 'r')
	md5searchlog2['line'] = md5searchlog2['obj'].readline()
	md5searchlog2['decomp'] = driveutils.decomposeFileLog(md5searchlog2['line'])
	md5searchlog2['last'] = None

	c=0

	while True:
		if md5searchlog['line'] is None:
			break
		if md5searchlog2['line'] is None:
			break
		if md5searchlog['line'].count(',') < 3:
			break
		if md5searchlog2['line'].count(',') < 3:
			break
		if md5searchlog['line']==md5searchlog['last']:
			break
		if md5searchlog2['line']==md5searchlog2['last']:
			break

		md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'])
		md5searchlog2['decomp'] = driveutils.decomposeFileLog(md5searchlog2['line'])
		print c,md5searchlog2['line'].rstrip()

		if md5searchlog['decomp']['sha'] == md5searchlog2['decomp']['sha']:
			rline2 = md5searchlog2['line']
			dupelog.write(rline2.rstrip()+"\n")
			print ' - dupe: ' + rline2.rstrip()

		c=c+1
		if md5searchlog['decomp']['sha'] >= md5searchlog2['decomp']['sha']:
			md5searchlog2['last'] = md5searchlog2['last']
			md5searchlog2['line'] = md5searchlog2['obj'].readline()
		else:
			md5searchlog['last'] = md5searchlog['last']
			md5searchlog['line'] = md5searchlog['obj'].readline()

	dupelog.close()
	driveutils.sortLogByPath(resultlog,0)


def findDupesInLog(md5log, resultlog, tmpfolder, runopts):

	driveutils.sortLogByPath(md5log,0)

	driveutils.createNewLog(resultlog,False)
	dupelog = open(resultlog, 'ab')

	md5searchlog = {}
	md5searchlog['obj'] = open(md5log, 'r')
	md5searchlog['line'] = md5searchlog['obj'].readline()
	md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'])

	lastmd5 = None
	with open(md5log) as f:
	    for rline in f.readlines():

			fileobj = driveutils.decomposeFileLog(rline)
			if lastmd5 is None:
				lastmd5 = fileobj['sha']
			elif lastmd5 == fileobj['sha']:
				continue

			print rline.rstrip()
			found=False

			while md5searchlog['decomp']['sha'] < fileobj['sha'] and md5searchlog['line'].rstrip() != '':
				md5searchlog['line'] = md5searchlog['obj'].readline()
				if md5searchlog['line'].rstrip() != '':
					md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'])
			while md5searchlog['decomp']['sha'] == fileobj['sha'] and md5searchlog['line'].rstrip() != '':
				rline2 = md5searchlog['line']
				if rline.rstrip() != rline2.rstrip():
					if found == False:
#						if 'skipthisfirst' in runopts.keys():
#							searchahead = open(md5log, 'r')
#							searchahead.seek(  md5searchlog['obj'].tell()  )
#							curline = searchahead.readline()
#							decomp = driveutils.decomposeFileLog(curline)

						if 'skipfirst' in runopts.keys():
							found=True
						else:
							dupelog.write(rline.rstrip()+"\n")
							found=True
					dupelog.write(rline2.rstrip()+"\n")
					print ' - dupe: ' + rline2.rstrip()
				md5searchlog['line'] = md5searchlog['obj'].readline()
				if md5searchlog['line'].rstrip() != '':
					md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'])

			lastmd5 = fileobj['sha']

	dupelog.close()
	driveutils.sortLogByPath(resultlog,0)

def buildALogOfDupes(md5log, resultlog, runopts=None):
	timestr = time.strftime("%Y%m%d-%H%M%S")

	tmpdir = ''
	if 'tmpdir' not in runopts.keys():
		tmpdir = "/tmp/"
	else:
		tmpdir = runopts['tmpdir']
	tmpdir += "/find_dupes/"+timestr+"/"

	if 'verslog' in runopts.keys():
		findDupesBetweenLogs(md5log, runopts['verslog'], resultlog, tmpdir, runopts)
	else:
		findDupesInLog(md5log, resultlog, tmpdir, runopts)

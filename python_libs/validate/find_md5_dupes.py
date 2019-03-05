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
	lastbasepath = None
	with open(md5log) as f:
	    for rline in f.readlines():

			fileobj = driveutils.decomposeFileLog(rline)
			# skip over any entries on the first file ptr already reviewed
			if lastbasepath is None:
				lastbasepath = fileobj['fullpath']
			if lastmd5 is None:
				lastmd5 = fileobj['sha']
			elif lastmd5 == fileobj['sha']:
				continue

			print rline.rstrip()
			found=False
			lastcheck=False
			if 'skipfirstpath' in runopts.keys() and re.match("^(.*?\/\/).*",lastbasepath):
				regex="^(.*?\/\/)"
				if 'skipfirstpathregex' in runopts.keys():
					regex=runopts['skipfirstpathregex']
				lastcheck=re.findall(regex,lastbasepath)[0]

			while md5searchlog['decomp']['sha'] < fileobj['sha'] and md5searchlog['line'].rstrip() != '':
				md5searchlog['line'] = md5searchlog['obj'].readline()
				if md5searchlog['line'].rstrip() != '':
					md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'])
			while md5searchlog['decomp']['sha'] == fileobj['sha'] and md5searchlog['line'].rstrip() != '':
				rline2 = md5searchlog['line']
				if rline.rstrip() != rline2.rstrip():
					if found == False:
						if 'skipfirst' in runopts.keys():
							found=True
						elif 'skipfirstpath' not in runopts.keys():
							dupelog.write(rline.rstrip()+"\n")
							found=True

					if 'skipfirstpath' in runopts.keys():
						if re.match("^(.*?\/\/).*",md5searchlog['decomp']['fullpath']):
							regex="^(.*?\/\/)"
							if 'skipfirstpathregex' in runopts.keys():
								regex=runopts['skipfirstpathregex']
							curcheck=re.findall(regex,md5searchlog['decomp']['fullpath'])[0]
							if lastcheck != curcheck:
								found=True
								dupelog.write(rline2.rstrip()+"\n")
						#print ' - dupe: ' + rline2.rstrip()
					else:
						dupelog.write(rline2.rstrip()+"\n")
						#print ' - dupe: ' + rline2.rstrip()

				md5searchlog['line'] = md5searchlog['obj'].readline()
				if md5searchlog['line'].rstrip() != '':
					md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'])

			lastmd5 = fileobj['sha']
			lastbasepath = fileobj['fullpath']

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

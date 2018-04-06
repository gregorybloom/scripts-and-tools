from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv, datetime



def findDupesInLog(md5log, resultlog, tmpfolder, runopts):

	driveutils.sortLogByPath(md5log,0)

	driveutils.createNewLog(resultlog,False)
	dupelog = open(resultlog, 'ab')

	md5searchlog = {}
	md5searchlog['obj'] = open(md5log, 'r')
	md5searchlog['line'] = md5searchlog['obj'].readline()
	md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'],1)

	lastmd5 = None
	with open(md5log) as f:
	    for rline in f.readlines():

			fileobj = driveutils.decomposeFileLog(rline,1)
			if lastmd5 is None:
				lastmd5 = fileobj['sha']
			elif lastmd5 == fileobj['sha']:
				continue

			print rline.rstrip()
			found=False

			while md5searchlog['decomp']['sha'] < fileobj['sha'] and md5searchlog['line'].rstrip() != '':
				md5searchlog['line'] = md5searchlog['obj'].readline()
				if md5searchlog['line'].rstrip() != '':
					md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'],1)
			while md5searchlog['decomp']['sha'] == fileobj['sha'] and md5searchlog['line'].rstrip() != '':
				rline2 = md5searchlog['line']
				if rline.rstrip() != rline2.rstrip():
					if found == False:
#						if 'skipthisfirst' in runopts.keys():
#							searchahead = open(md5log, 'r')
#							searchahead.seek(  md5searchlog['obj'].tell()  )
#							curline = searchahead.readline()
#							decomp = driveutils.decomposeFileLog(curline,1)

						elif 'skipfirst' in runopts.keys():
							found=True
						else:
							dupelog.write(rline.rstrip()+"\n")
							found=True
					dupelog.write(rline2.rstrip()+"\n")
					print ' - dupe: ' + rline2.rstrip()
				md5searchlog['line'] = md5searchlog['obj'].readline()
				if md5searchlog['line'].rstrip() != '':
					md5searchlog['decomp'] = driveutils.decomposeFileLog(md5searchlog['line'],1)

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
	findDupesInLog(md5log, resultlog, tmpdir, runopts)

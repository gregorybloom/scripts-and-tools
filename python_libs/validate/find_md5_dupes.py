from maintenance_loader import *

import os, sys, hashlib, time, shutil, re
import csv, datetime



def findDupesInLog(md5log, resultlog, tmpfolder):

	driveutils.sortLogByPath(md5log,0)

	driveutils.createNewLog(resultlog,False)
	dupelog = open(resultlog, 'ab')

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
			with open(md5log) as f2:
			    for rline2 in f2.readlines():
					if rline == rline2:
						continue
					fileobj2 = driveutils.decomposeFileLog(rline2,1)

					if fileobj['sha'] == fileobj2['sha']:
						if found == False:
							dupelog.write(rline.rstrip()+"\n")
							found=True
						dupelog.write(rline2.rstrip()+"\n")
						print ' - dupe: ' + rline2.rstrip()

			lastmd5 = fileobj['sha']

	dupelog.close()
	driveutils.sortLogByPath(resultlog,0)


def buildALogOfDupes(md5log, resultlog, tmpdir=None):
	timestr = time.strftime("%Y%m%d-%H%M%S")

	if tmpdir is None:
		tmpdir = "/tmp/"
	tmpdir += "/find_dupes/"+timestr+"/"
	findDupesInLog(md5log, resultlog, tmpdir)

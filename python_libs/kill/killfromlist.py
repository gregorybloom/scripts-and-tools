
import os, sys, hashlib, time, re
from maintenance_loader import *


def killFromList(filelist):
	logF = open(filelist, 'rb')
	
	while 1:
		line = logF.readline()
		if not line:
			break

		path='notapathx'
		
		reg = r'^[A-Za-z0-9*]+, [0-9*]+,'
		if re.search(reg,line):
			obj = driveutils.decomposeFileLog(line,1)
			path = obj['fullpath']
		else:
			path=line.strip()

		if( len(path)>5 ):
                    if( not path.startswith("// ") ):
			if(  os.path.exists(path)  ):
				if( os.path.islink(path) ):
					continue
				if(  not os.path.isdir(path)  ):
					print 'deleting: '+ path
					try:
						os.remove(path)
						continue
					except OSError as exception:
						print '** err on '+str(exception)
						continue
					
				else:
					print '- skipping dir: '+path
			else:
				print '- not found: '+ path
		
	




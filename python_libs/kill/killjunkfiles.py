
import os, sys, hashlib, time, re, shutil
from maintenance_loader import *

killfolders=True

def killJunkFiles(basePath):
	walkFoldersForJunk(basePath, '')

def walkFoldersForJunk(base, path):
	global killfolders
	files = driveutils.readDir(base+'/'+path)
	for file in files:
		namestr= base+'/'+path+str(file)
		
		if( os.path.islink(namestr) ):
			continue
		if(  not os.path.exists(namestr)  ):
			continue

		if(  os.path.isdir(namestr)  ):
#                        if( path==""):
#                            print str(file)
			if( path=="" ) and (str(file)==".Trashes"):
				continue
				
			walkFoldersForJunk(base,path+file+'/')
		else:
			
			namef = str(file)
#			print '- '+ namestr
			
			purge = False
			if(namef == '._.DS_Store'):
				purge = True
			if(namef == '.DS_Store'):
				purge = True
			if(namef == '.localized'):
				purge = True
			if(namef == 'Icon'):
				purge = True
			if(namef == 'ICON'):
				purge = True
			if(namef.startswith('._')):
				purge = True
			if(namef.startswith('.~')):
				purge = True


			if purge == True:
				print 'deleting: '+ namestr
				try:
					os.remove(namestr)
###					shutil.rmtree(namestr)	# kills files too
				except OSError as exception:
					print '** err on '+namestr
					continue
	return


import os, sys, hashlib, time, re, shutil
from maintenance_loader import *
from folderlist import *

killfolders=True

def killEmptyFolders(basePath):
	checkWalks(basePath)


def checkWalks(base):
	global killfolders
	
	d=0
	purged=True
	while purged:
		purged=walkFolders(base, "")
		if purged:
			print "---------------------------------------------------------"
			print "-------------------RUN AGAIN: "+str(d)+" ---------------------"
			print "---------------------------------------------------------"
		d=d+1
		if not killfolders:
			break


def walkFolders(base, path):
	global killfolders
	purged=False
	files = driveutils.readDir(base+'/'+path)
	for file in files:
		namestr= base+'/'+path+str(file)
		
		if( os.path.islink(namestr) ):
			continue
		if(  not os.path.exists(namestr)  ):
			continue
		if(  os.path.isdir(namestr)  ):
			if( path=="" ) and (str(file)==".Trashes"):
				continue
			c=countContents(namestr)

			
#			print '- '+ namestr + ' '+str(c) +'  '  +', '.join(os.listdir(namestr))

			if (c<1):
				purged=True
				print 'deleting: '+ namestr + ' '+str(c)
				
				if killfolders:
					try:
###						os.remove(namestr)
						shutil.rmtree(namestr)	# kills files too
					except OSError as exception:
#						print '** err on '+str(exception)
						continue
					
			else:
				purged = purged | walkFolders(base,path+file+'/')
	return purged

def countContents(path):
	c=0
#	x=''
	files = driveutils.readDir(path)
	for file in files:
#		x=x+' '+str(file)
		c=c+1
#	print x
	return c

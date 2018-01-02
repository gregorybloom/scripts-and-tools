
import os, sys, hashlib, time, re
from maintenance_loader import *



logfolder = "logs"

hashes = {}
groups = {}
gd=0



def beginWalkForDiff(pathA, pathB, logname):
    driveutils.createNewLog(logfolder+'/'+ logname)


    walkForDiff(pathA, pathB, '', logname)


def walkForDiff(pathA, pathB, step, logname):
    global logfolder

    filesA = []
    filesB = []

    if(  os.path.exists(pathA+'/'+ step)  ):
        filesA = driveutils.readDir( pathA+'/'+ step )
    if(  os.path.exists(pathB+'/'+ step)  ):
        filesB = driveutils.readDir( pathB+'/'+ step )

    fileList = filesA = filesB
    fileList = sorted(set(fileList))


    print '. '+step

    for file in fileList:

        curPathA = pathA+'/'+ step + file
        curPathB = pathB+'/'+ step + file

        objA={}
        objB={}
        if( os.path.exists(curPathA) and not os.path.isdir(curPathA) ):
            objA = driveutils.getFileInfo( curPathA )

        if( os.path.exists(curPathB) and not os.path.isdir(curPathB) ):
            objB = driveutils.getFileInfo( curPathB )



        if( not os.path.exists(curPathA) and os.path.exists(curPathB)  ):

            if(  os.path.isdir(curPathB)  ):
                walkForDiff(pathA, pathB, step+file+'/', logname)
            else:
                print '+ ' +objB['fullpath']
                driveutils.addToLog( '+ ' +objB['fullpath']+'\n', logfolder+'/'+ logname )

        if( os.path.exists(curPathA) and not os.path.exists(curPathB)  ):

            if(  os.path.isdir(curPathA)  ):
                walkForDiff(pathA, pathB, step+file+'/', logname)
            else:
                print '- ' +objA['fullpath']
                driveutils.addToLog( '- ' +objA['fullpath']+'\n', logfolder+'/'+ logname )

        if( os.path.exists(curPathA) and os.path.exists(curPathB)  ):

            if(  os.path.isdir(curPathA)  ):
                walkForDiff(pathA, pathB, step+file+'/', logname)
            else:

                if not finddupes.comparegroup(objA, objB):
                    print '% ' +objB['fullpath']
                    driveutils.addToLog( '% ' +objB['fullpath']+'\n', logfolder+'/'+ logname )

	

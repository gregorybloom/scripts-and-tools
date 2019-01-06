import re,os,json,sys,shutil,imp
from datetime import datetime
#  DB parsing script #5
#  debug campaign threads
#       afterwords, build the posts!
#           - buildposts.py


SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/config/herobuildconf.py')


_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT




threadlist={}
for subdir, dirs, files in os.walk(_COREPATH + "/campaigns"):
    for file in files:
        if re.match(".*\W+posts\W+x(?:story|message)post\W+postdata\W+js$", subdir):

            filepath = subdir + os.sep + file

            groupsA = re.findall(".*\W+campaigns\W+(\w+)\W+posts\W+x(?:story|message)post\W+postdata\W+js$", subdir)
            groupsB = re.findall("(\d+)\.js$", file)
            groupsC = re.findall(".*\W+campaigns\W+\w+\W+posts\W+(x(?:story|message)post)\W+postdata\W+js$", subdir)

            if len(groupsA) > 0 and len(groupsB) > 0 and len(groupsC) > 0:
                campaignid = groupsA.pop()
                threadid = groupsB.pop()
                threadtype = groupsC.pop()

                if campaignid not in threadlist.keys():
                    threadlist[campaignid]={}
                if threadtype not in threadlist[campaignid].keys():
                    threadlist[campaignid][threadtype]={}

                threadlist[campaignid][threadtype][threadid]=filepath
                print campaignid, threadtype, threadid, filepath


#        if filepath.endswith(".asm"):
 #           print (filepath)





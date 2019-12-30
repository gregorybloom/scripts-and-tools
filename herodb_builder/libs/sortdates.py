from datetime import datetime as dt
import re,os,json,sys,shutil,imp,datetime
import pprint

SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))

heroconf = imp.load_source('heroconf', SCRIPTPATH+'/../config/herobuildconf.py')
_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT


def compareDates(date1str,date2str):
    #"postdate": "2004-07-18 14:51:04-07",
    saveddate1 = re.findall("^([\d\-]{10}\s*[\d\:]{8})", date1str).pop()
    saveddate2 = re.findall("^([\d\-]{10}\s*[\d\:]{8})", date2str).pop()
    date1 = datetime.datetime.strptime(saveddate1, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.datetime.strptime(saveddate2, '%Y-%m-%d %H:%M:%S')
    if date2 > date1:
        return True
    return False

def buildDateSortedKeys(threadset,type):
    threadkeys=json.loads(json.dumps(threadset.keys()))
    sortedkeys=[]
    infcheck=0
    while len(threadkeys) > 0:
        lowestdate=None
        lowestkey=None
        lowesti=None
        curi=0
        for key in threadkeys:

            curdate=None
            if type == 'posts' and '_postdata' in threadset[key].keys():
                curdate=threadset[key]['_postdata']['postdate']
            elif type == 'list':
                curdate=threadset[key]['postdate']

            if curdate is not None:
                setnew = False
                if lowestdate is None:
                    setnew = True
                elif not compareDates(lowestdate,curdate):
                    setnew = True

                if setnew:
                    lowestdate = curdate
                    lowestkey = key
                    lowesti = curi
            else:
                print "DATE SORT ERROR",key,threadset[key]
                sys.exit(1)
            curi+=1

        if lowestdate:
            del threadkeys[lowesti]
            sortedkeys.append(lowestkey)
        else:
            print "DATE SORT ERROR X",threadkeys
            sys.exit(1)

        infcheck+=1
        if infcheck > 2*len(threadset.keys()):
            print "DATE INF SORT ERROR X",threadkeys
            sys.exit(1)

    return sortedkeys

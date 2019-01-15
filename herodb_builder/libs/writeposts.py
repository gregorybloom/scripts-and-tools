from datetime import datetime as dt
import re,os,json,sys,shutil,imp
import pprint

SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
filtertext = imp.load_source('filtertext', SCRIPTPATH+'/libs/filtertext.py')
sortdates = imp.load_source('sortdates', SCRIPTPATH+'/libs/sortdates.py')


heroconf = imp.load_source('heroconf', SCRIPTPATH+'/config/herobuildconf.py')
_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT


def writeStaticPostFileText(writefile,threadset,campaignuserdata,campaigncharacterdata,depth):
    if 'userid' in threadset['_postdata'].keys():
        userid = threadset['_postdata']['userid']

    username = None
    charname = None
    if userid in campaignuserdata.keys():
        username = campaignuserdata[userid]['displayname']
    if userid in campaigncharacterdata.keys():
        charname = campaigncharacterdata[userid]['charactername']

    linkstr = ""
    linkstr += "<div class='postframe'>\n"
    linkstr += "<div class='postcontent'>\n"
    linkstr += "<div class='posthead'>\n"

    linkstr += "<div class='posttitle'>\n"
    linkstr += filtertext.filterEntry( threadset['_postdata']['posttitle'], 'posttitle' )
    linkstr += "</div>\n"
    linkstr += "<div class='postchar'>\n"
    linkstr += filtertext.filterEntry( charname, 'charname' )
    linkstr += "</div>\n"
    linkstr += "<div class='postuser'>\n"
    linkstr += filtertext.filterEntry( username, 'username' )
    linkstr += "</div>\n"
    linkstr += "<div class='postdate'>\n"
    linkstr += filtertext.filterEntry( threadset['_postdata']['postdate'], 'postdate' )
    linkstr += "</div>\n"

    linkstr += "</div>\n"
    linkstr += "<div class='posttext'>\n"
    linkstr += filtertext.filterEntry( threadset['_postdata']['postcontent'], 'postcontent' )
    linkstr += "</div>\n"

    linkstr += "</div>\n"
    linkstr += "<div class='postsubposts'>\n"
    writefile.write(linkstr.encode("utf-8"))

    if '_subposts' in threadset.keys():
        datesortedkeys = sortdates.buildDateSortedKeys(threadset['_subposts'],'posts')
        for key in datesortedkeys:
            writeStaticPostFileText(writefile,threadset['_subposts'][key],campaignuserdata,campaigncharacterdata,(depth+1))

    linkstr = ""
    linkstr += "</div>\n"
    linkstr += "</div>\n"
    writefile.write(linkstr.encode("utf-8"))


def fillStaticPostFile(campaignid,posttype,roottreeid,writefile,posttreedata,campaignuserdata,campaigncharacterdata):
    jsonpath = _COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/json/" + roottreeid + ".json"
    if os.path.exists(jsonpath):

        rootthreaddata=None
        with open(jsonpath, 'r') as f:
            for line in f:
                rootthreaddata = json.loads(line.rstrip())

        writeStaticPostFileText(writefile,rootthreaddata,campaignuserdata,campaigncharacterdata,0)

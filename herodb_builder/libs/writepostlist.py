from datetime import datetime as dt
import re,os,json,sys,shutil,imp
import pprint


SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
filtertext = imp.load_source('filtertext', SCRIPTPATH+'/libs/filtertext.py')
sortdates = imp.load_source('sortdates', SCRIPTPATH+'/libs/sortdates.py')

heroconf = imp.load_source('heroconf', SCRIPTPATH+'/../config/herobuildconf.py')
_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT

def fillStaticListFile(campaignid,posttype,writefile,posttreedata,campaignuserdata,campaigncharacterdata,rootthreadset):

    rootbydate={}

    datesortedkeys=sortdates.buildDateSortedKeys(rootthreadset,'list')
    for key in datesortedkeys:

        roottreeid = key
        userid = None
        username = None
        charname = None
        if roottreeid not in rootthreadset.keys():
            print "thread not found!", campaignid,posttype,roottreeid


        if 'userid' in rootthreadset[roottreeid].keys():
            userid = rootthreadset[roottreeid]['userid']

        if userid in campaignuserdata.keys():
            username = campaignuserdata[userid]['displayname']
        if userid in campaigncharacterdata.keys():
            charname = campaigncharacterdata[userid]['charactername']


        path = _COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/" + roottreeid + ".html"
        linkstr = ""
        linkstr += "<div class='linkdiv'>\n"
        linkstr += "<div class='linkdivfront'>\n"
        linkstr += "<a href='posts/static/"+ posttype +"/"+ roottreeid +".html'>\n"
        linkstr += "posts/static/"+ posttype +"/"+ roottreeid +".html\n"
        linkstr += "</a>\n"
        linkstr += "<span class='linkdivtitle'>\n"
        linkstr += filtertext.filterEntry( rootthreadset[roottreeid]['posttitle'], 'posttitle' )
        linkstr += "</span>\n"
        linkstr += "</div>\n"
        linkstr += "<div class='linkdivback'>\n"
        linkstr += "<span class='linkchar'>"
        linkstr += filtertext.filterEntry( charname, 'charname' )
        linkstr += "</span>\n"
        linkstr += "<span class='linkuser'>"
        linkstr += filtertext.filterEntry( username, 'username' )
        linkstr += "</span>\n"
        linkstr += "<div class='linkdivdate'>\n"
        linkstr += filtertext.filterEntry( rootthreadset[roottreeid]['postdate'], 'postdate' )
        linkstr += "</div>\n"
        linkstr += "</div>\n"
        linkstr += "</div>\n"

        writefile.write(linkstr.encode("utf-8"))

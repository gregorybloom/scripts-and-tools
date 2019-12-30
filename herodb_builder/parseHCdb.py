import re,os,json,sys,imp
#  DB parsing script #0
#  parses the DB
#       afterwords, parse the posts!
#        - parseposttree.py



SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/../config/herobuildconf.py')


_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT

if not os.path.exists(_COREPATH):
    os.makedirs(_COREPATH)

if not os.path.exists(_COREPATH+"/tabledump"):
    os.makedirs(_COREPATH+"/tabledump")
if not os.path.exists(_COREPATH+"/infodump"):
    os.makedirs(_COREPATH+"/infodump")






def filterOutput(tablename,tabledata):
    deleteentries = []
    if tablename == "xcharacter":
        deleteentries=["sendstoryposts","characteremail","sendcampaignedits","sendcampaignposts","sendstoryedits"]
    if tablename == "xcampaign":
        deleteentries=["storyboardsoundlocation"]
    if tablename == "xuser":
        deleteentries=['password','md5password','email','displayemail','aim','msn','icq','yahoo','timezone','realname','startpage']
        deleteentries.extend(['siteadmin', 'usesound', 'emailprivatemessages', 'emailgeneralmessages', 'emailgeneralmessageedits'])
        deleteentries.extend(['defaultcampaignid', 'hidenewposts', 'hideoldposts'])

    if len(deleteentries) > 0:
        for k in deleteentries:
            tabledata.pop(k, None)



tablelist=["xcampaign","xcharacter","xmessagepost","xmessagepostemailid","xmessagepostviewtime","xnonplayercharacter","xpremiumfile","xpremiumsettings","xprivatemessage","xquotes","xsiterecords","xstorypost","xstorypostemailid","xstorypostviewtime","xstorypostvisibility","xtimeline","xuser","xuseraccess","xuserstyle","messages","users"]
tablelist.remove('xuserstyle')          # not useful
tablelist.remove('xuseraccess')          # not useful
tablelist.remove('xstorypostviewtime')  # not useful
tablelist.remove('xsiterecords')  # not useful
tablelist.remove('xpremiumsettings')  # not useful
tablelist.remove('users')  # not useful
tablelist.remove('messages')  # not useful
tablelist.remove('xmessagepostemailid')  # not useful
tablelist.remove('xstorypostemailid')  # not useful
tablelist.remove('xmessagepostviewtime')  # not useful
tablelist.remove('xpremiumfile')  # not useful
# xprivatemessage (privatemessageid, touserid, fromuserid, senddate, viewdate, subject, content, senderdeletedate, recipientdeletedate, folder)
tablelist.remove('xprivatemessage')  # security


# xcampaign (campaignid, campaignname, userid, campaigndescription, isactive, subname, acceptingplayers, campaignsummary, campaigncategory, storyboardsoundlocation, creationdate)
# xcharacter (userid, campaignid, charactername, characterquote, imagelocation, hdclocation, avatarlocation, otherinfo, characteremail, isgm, isactive, sendstoryposts, sendstoryedits, sendcampaignposts, sendcampaignedits, status)
# xmessagepost (messagepostid, userid, postdate, posttitle, postcontent, parentid, progenitorid, campaignid, category, lockedlocation)
# xnonplayercharacter (nonplayercharacterid, campaignid, name, hdcfilelocation, imagelocation, info, quote)
# xquotes (quoteid, campaignid, quote, byline, "position")
# xstorypost (storypostid, userid, campaignid, postdate, posttitle, postcontent, parentid, progenitorid, filelocation, ignorevisibility, lockedlocation, charactername)
# xstorypostvisibility (userid, storypostid)
# xtimeline (timelineid, campaignid, entry, dateline, "position")
# xuser (userid, username, displayname, personalinfo, status)



writefile=None

tablename=None
tableinfo={}
mode="find"
with open('hero_central', 'r') as f:
  for line in f:

     if mode == "save":
         if re.match("^ALTER TABLE ONLY \w+", line):
            mode="find"
         if re.match("^SELECT \w+\.\w+\(", line):
            mode="find"

     if mode in ["find","save"] and re.match("^COPY \w+ \(", line):
         mode="find"
         groups=re.findall("^COPY (\w+) \(", line)
         tablename=groups[0] if len(groups) > 0 else None
         print line
         labelgroup = re.findall("^COPY \w+ \(([^\(\)]+)\)", line)
         labelsetO = labelgroup[0].split(",") if len(labelgroup) > 0 else None
         if labelsetO:
             tableinfo={}
             labelset=[x.lstrip() for x in labelsetO]
             tableinfo['tablename']=tablename
             tableinfo['labelset']=labelset
             if tablename and tablename in tablelist:
                 mode="save"

                 if writefile:
                     writefile.close()
                 writefile = open(_COREPATH+"/tabledump/"+tablename+'.txt', 'w')
         continue


     if mode == "save" and re.match("\w+", line):
         linedataO=line.split("\t")
         linedata=[x.rstrip() for x in linedataO]
         if len(linedata) == len(tableinfo['labelset']) and len(linedata) > 0 and writefile:
             tableinfo['tabledata']=dict(zip(tableinfo['labelset'],linedata))
             labelset=tableinfo.pop('labelset')
             filterOutput(tableinfo['tablename'],tableinfo['tabledata'])
             json.dump(tableinfo['tabledata'], writefile)
             writefile.write("\n")
             tableinfo['labelset']=labelset

         else:
             print 'CRITICAL ERROR'
             print len(tableinfo), len(linedata)
             print tableinfo
             print linedata
             print line
             break


if writefile:
    writefile.close()



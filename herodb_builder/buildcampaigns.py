import re,os,json,sys,shutil,imp
#  DB parsing script #4
#  parses the campaign data
#       afterwords, debug the campaigns
#           - debugcampaigns.py




SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/config/herobuildconf.py')


_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT






justpushtemplates=False

def writeUserData(campaignid,userid,userdata):
    campaignpath = _COREPATH + "/campaigns/" + campaignid
    if not os.path.exists(campaignpath + "/_data/users/json/"):
        os.makedirs(campaignpath + "/_data/users/json/")
    if not os.path.exists(campaignpath + "/_data/users/js/"):
        os.makedirs(campaignpath + "/_data/users/js/")
    writefile = open(campaignpath + "/_data/users/json/"+userid+".json", 'w')
    if writefile:
        json.dump(userdata,writefile)
        writefile.close()
    writefile = open(campaignpath + "/_data/users/js/"+userid+".js", 'w')
    if writefile:
        stringdata = 'var JSONDATA_USER_'+userid+' = ' + json.dumps(userdata) + ';'
        writefile.write(stringdata)
        writefile.close()
def writeCharacterData(campaignid,characterid,characterdata):
    campaignpath = _COREPATH + "/campaigns/" + campaignid
    if not os.path.exists(campaignpath + "/_data/characters/json/"):
        os.makedirs(campaignpath + "/_data/characters/json/")
    if not os.path.exists(campaignpath + "/_data/characters/js/"):
        os.makedirs(campaignpath + "/_data/characters/js/")
    writefile = open(campaignpath + "/_data/characters/json/"+characterid+".json", 'w')
    if writefile:
        json.dump(characterdata,writefile)
        writefile.close()
    writefile = open(campaignpath + "/_data/characters/js/"+characterid+".js", 'w')
    if writefile:
        stringdata = 'var JSONDATA_CHAR_'+characterid+' = ' + json.dumps(characterdata) + ';'
        writefile.write(stringdata)
        writefile.close()







campaigninfopath = _COREPATH + "/infodump/campaignlist.txt"
writefile = open(campaigninfopath, 'w')
if writefile:
    with open(_COREPATH+"/tabledump/xcampaign.txt", 'r') as f:
      for line in f:
        campaigndata = json.loads(line.rstrip())
        if re.match("^\\*N$",campaigndata['campaignid']):
            campaigndata['campaignid']='N'

        writefile.write(campaigndata['campaignid']+', '+campaigndata['campaignname']+"\n")
        print 'write:', campaigndata['campaignid']+', '+campaigndata['campaignname']


if not os.path.exists(_COREPATH+"/campaigns/"):
    os.makedirs(_COREPATH+"/campaigns/")
if os.path.exists(_COREPATH+"/campaigns/campaignlist.txt"):
    os.remove(_COREPATH+"/campaigns/campaignlist.txt")
if not os.path.exists(_COREPATH+"/campaigns/campaignlist.txt"):
    shutil.copyfile(campaigninfopath, _COREPATH+"/campaigns/campaignlist.txt")





with open(_COREPATH+"/tabledump/xcampaign.txt", 'r') as f:
  for line in f:
    campaigndata = json.loads(line.rstrip())
    if re.match("^\\*N$",campaigndata['campaignid']):
        campaigndata['campaignid']='N'

    campaignpath = _COREPATH + "/campaigns/" + campaigndata['campaignid']
    if not os.path.exists(campaignpath):
        os.makedirs(campaignpath)


    if os.path.exists(SCRIPTPATH+"/templates/_template"):
        templatefolderpath=_COREPATH + "/campaigns/" + campaigndata['campaignid'] + "/_template"
        if os.path.exists(templatefolderpath):
            shutil.rmtree(templatefolderpath,ignore_errors=True)
        shutil.copytree(SCRIPTPATH+"/templates/_template", _COREPATH + "/campaigns/" + campaigndata['campaignid'] + "/_template")



    userdata=None
    if os.path.exists(_TMPPATH+"/tmp/users/"+campaigndata['userid']+".txt"):
        with open(_TMPPATH+"/tmp/users/"+campaigndata['userid']+".txt", 'r') as f:
            for line in f:
                userdata=json.loads(line.rstrip())
    else:
        print "CRASH sdf"
        sys.exit(1)
    if userdata is not None:
        writeUserData(campaigndata['campaignid'],campaigndata['userid'],userdata)






    if not justpushtemplates:
        usercharlibrary={}
        usercharlibrary['chars']={}
        usercharlibrary['users']={}

        campaigndata['campaignsummary']=campaigndata['campaignsummary'].replace("\\r\\n","\n")
        campaigndata['campaigndescription']=campaigndata['campaigndescription'].replace("\\r\\n","\n")
        writefile = open(campaignpath + "/infopage.txt", 'w')
        if writefile:
            writefile.write('campaign name: '+campaigndata['campaignname']+"\n")
            writefile.write('campaign byline: '+campaigndata['subname'].encode('utf-8')+"\n")
            writefile.write('created by: '+userdata['displayname']+"\n")
            writefile.write('created on: '+campaigndata['creationdate']+"\n")
            writefile.write('campaign type: '+campaigndata['campaigncategory']+"\n")
            writefile.write("------------------------\n")
            writefile.write(campaigndata['campaignsummary'].encode('utf-8')+"\n")
            writefile.write("------------------------\n")
            writefile.write(campaigndata['campaigndescription'].encode('utf-8')+"\n")
            writefile.close()


        if os.path.exists(_TMPPATH+"/tmp/characters/"+campaigndata['campaignid']):
            characterlist=[]
            for filename in os.listdir(_TMPPATH+"/tmp/characters/"+campaigndata['campaignid']):
                with open(_TMPPATH+"/tmp/characters/"+campaigndata['campaignid']+"/"+filename, 'r') as f:
                    for line in f:
                        characterdata = json.loads(line.rstrip())
                        characterlist.append(characterdata)

            writefile = open(campaignpath + "/characters.txt", 'w')
            if writefile:
                for characterdata in characterlist:
                    userdata = None
                    if os.path.exists(_TMPPATH + "/tmp/users/" + characterdata['userid'] + ".txt"):
                        with open(_TMPPATH + "/tmp/users/" + characterdata['userid'] + ".txt", 'r') as f:
                            for line in f:
                                userdata = json.loads(line.rstrip())
                    else:
                        print "CRASH sdf"
                        sys.exit(1)
                    if userdata is not None:
                        writeUserData(campaigndata['campaignid'], characterdata['userid'], userdata)
                        usercharlibrary['users'][characterdata['userid']]=characterdata['userid'];

                    writefile.write('character name: '+characterdata["charactername"].encode('utf-8')+"\n")
                    writefile.write('played by: '+userdata["displayname"].encode('utf-8')+"\n")
                    if characterdata["isgm"] == "Y":
                        writefile.write("Game GM\n")
                    writefile.write('character quote: '+characterdata["characterquote"].encode('utf-8')+"\n")
                    writefile.write("------------------------\n")
                    writefile.write('description: '+characterdata['otherinfo'].encode('utf-8')+"\n")
                    writefile.write("************************\n")

                    if characterdata is not None:
                        writeCharacterData(campaigndata['campaignid'], characterdata['userid'], characterdata)
                        usercharlibrary['chars'][characterdata['userid']]=characterdata['userid'];


        print campaignpath + "/_data/lists/json/" + "/userlist.json"
        if not os.path.exists(campaignpath + "/_data/lists/json/"):
            os.makedirs(campaignpath + "/_data/lists/json/")
        if not os.path.exists(campaignpath + "/_data/lists/js/"):
            os.makedirs(campaignpath + "/_data/lists/js/")
        writefile = open(campaignpath + "/_data/lists/json/" + "/userlist.json", 'w')
        if writefile:
            json.dump(usercharlibrary, writefile)
            writefile.close()
        writefile = open(campaignpath + "/_data/lists/js/" + "/userlist.js", 'w')
        if writefile:
            stringdata = 'var JSONDATA_USERLIST = ' + json.dumps(usercharlibrary) + ';'
            writefile.write(stringdata)
            writefile.close()


        if os.path.exists(_TMPPATH+"/tmp/quotes/"+campaigndata['campaignid']):
            quotelist={}
            for filename in os.listdir(_TMPPATH+"/tmp/quotes/"+campaigndata['campaignid']):
                with open(_TMPPATH+"/tmp/quotes/"+campaigndata['campaignid']+"/"+filename, 'r') as f:
                    for line in f:
                        quotedata = json.loads(line.rstrip())
                        print 'quote:', quotedata
                        quotelist[quotedata['\"position\"']] = quotedata

            writefile = open(campaignpath + "/quotes.txt", 'w')
            if writefile:
                quotearray2=quotelist.keys()
                quotearray=sorted(quotearray2, key=lambda x: int(x))

                for quotenum in quotearray:
                    quotedata=quotelist[str(quotenum)]

                    quotedata['quote'] = quotedata['quote'].replace("\\r\\n", "\n")
                    quotedata['byline'] = quotedata['byline'].replace("\\r\\n", "\n")
                    writefile.write('quote: ' + quotedata['quote'].encode('utf-8') + "\n")
                    writefile.write('byline: ' + quotedata['byline'].encode('utf-8') + "\n")
                    writefile.write("------------------------\n")
                writefile.close()


        if os.path.exists(_TMPPATH+"/tmp/timeline/"+campaigndata['campaignid']):
            timelinelist={}
            for filename in os.listdir(_TMPPATH+"/tmp/timeline/"+campaigndata['campaignid']):
                with open(_TMPPATH+"/tmp/timeline/"+campaigndata['campaignid']+"/"+filename, 'r') as f:
                    for line in f:
                        timelinedata = json.loads(line.rstrip())
                        print 'timeline:', timelinedata
                        timelinelist[timelinedata['\"position\"']] = timelinedata

            writefile = open(campaignpath + "/timeline.txt", 'w')
            if writefile:
                timelinearray2=timelinelist.keys()
                timelinearray=sorted(timelinearray2, key=lambda x: int(x))

                for timelinenum in timelinearray:
                    timelinedata=timelinelist[str(timelinenum)]

                    timelinedata['entry'] = timelinedata['entry'].replace("\\r\\n", "\n")
                    writefile.write('entry: ' + timelinedata['entry'].encode('utf-8') + "\n")
                    timelinedata['dateline'] = timelinedata['dateline'].replace("\\r\\n", "\n")
                    writefile.write('dateline: ' + timelinedata['dateline'].encode('utf-8') + "\n")
                    writefile.write("------------------------\n")
                writefile.close()





    posttype=['xstorypost','xmessagepost']
    for posttype in posttype:

        postset=['static','dynamic']
        for set in postset:
            if not os.path.exists(_COREPATH + "/campaigns/" + campaigndata['campaignid'] + "/posts/" +set+ "/"+ posttype):
                os.makedirs(_COREPATH + "/campaigns/" + campaigndata['campaignid'] + "/posts/" +set+ "/"+ posttype)

            if os.path.exists(SCRIPTPATH+"/templates/posts/posttemplate"):
                templatefolderpath=_COREPATH + "/campaigns/" + campaigndata['campaignid'] + "/posts/" +set+ "/"+ posttype +"/posttemplate"
                if os.path.exists(templatefolderpath):
                    shutil.rmtree(templatefolderpath, ignore_errors=True)
                if not os.path.exists(templatefolderpath):
                    shutil.copytree(SCRIPTPATH+"/templates/posts/posttemplate", templatefolderpath)

#    if not os.path.exists(campaignpath + "/gameposts"):
#        os.makedirs(campaignpath + "/gameposts")

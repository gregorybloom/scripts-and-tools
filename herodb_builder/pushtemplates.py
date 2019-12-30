import os,re,shutil,sys,imp,time

#  DB parsing script #7
#  pushes the templates
#       afterwords, use the campaign zipper to find and zip campaigns
#           - zipcampaign.sh


SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/../config/herobuildconf.py')
writeposts = imp.load_source('writeposts', SCRIPTPATH+'/libs/writeposts.py')
writepostlist = imp.load_source('writepostlist', SCRIPTPATH+'/libs/writepostlist.py')
loadusers = imp.load_source('loadusers', SCRIPTPATH+'/libs/loadusers.py')
loadposts = imp.load_source('loadposts', SCRIPTPATH+'/libs/loadposts.py')


_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT


timestr = time.strftime("%Y%m%d_%H%M%S")

runopts={}

arglist=sys.argv[1:]
print arglist
if "campaignid" in arglist:
    pt=arglist.index("campaignid")+1
    if pt < len(arglist):
        if re.match("^[\d,]+$",arglist[pt]):
            astr = arglist[pt]
            strarr = []
            if astr.find(',') > -1:
                alist = astr.split(",")
                for aitem in alist:
                    if re.match("^\d+$",aitem):
                        strarr.append(aitem)
            else:
                strarr=[astr]
            runopts['campaignid']=strarr
if "templateonly" in arglist:
    runopts['templateonly']=True


posttypes=['xstorypost','xmessagepost']
for filename in os.listdir(_COREPATH+"/campaigns/"):
    if re.match('^\d+$',filename) and os.path.isdir(_COREPATH+"/campaigns/"+filename):
        campaignid=filename


        if 'campaignid' in runopts.keys():
            if campaignid not in runopts['campaignid']:
                continue


        postsets=['dynamic', 'static']
        for set in postsets:

            for posttype in posttypes:
                print 'making: ',_COREPATH + "/campaigns/" + campaignid, set, posttype
                if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/" + set + "/" + posttype):
                    os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/" + set + "/" + posttype)

                if os.path.exists(SCRIPTPATH + "/templates/_template"):
                    templatefolderpath = _COREPATH + "/campaigns/" + campaignid + "/_template"
                    if os.path.exists(templatefolderpath):
                        shutil.rmtree(templatefolderpath, ignore_errors=True)
                    if not os.path.exists(templatefolderpath):
                        shutil.copytree(SCRIPTPATH + "/templates/_template", templatefolderpath)
                if os.path.exists(SCRIPTPATH + "/templates/posts/posttemplate"):
                    templatefolderpath=_COREPATH + "/campaigns/" + campaignid + "/posts/" + set + "/" + posttype +"/posttemplate"
                    if os.path.exists(templatefolderpath):
                        shutil.rmtree(templatefolderpath, ignore_errors=True)
                    if not os.path.exists(templatefolderpath):
                        shutil.copytree(SCRIPTPATH + "/templates/posts/posttemplate", templatefolderpath)


if 'templateonly' in runopts.keys():
    if runopts['templateonly']:
        sys.exit(0)


for filename in os.listdir(_COREPATH+"/campaigns/"):
    if re.match('^\d+$',filename) and os.path.isdir(_COREPATH+"/campaigns/"+filename):
        campaignid=filename

        if 'campaignid' in runopts.keys():
            if campaignid not in runopts['campaignid']:
                continue

        campaignuserdata=loadusers.loadUserInfo(_COREPATH,campaignid,'users')
        campaigncharacterdata=loadusers.loadUserInfo(_COREPATH,campaignid,'characters')


        postsets=['dynamic', 'static']
        for set in postsets:

            posttreedata = loadposts.loadPostsFromCampaignData(campaignid)
            for posttype in posttypes:

                for threadname in os.listdir(_COREPATH + "/campaigns/" + campaignid + "/posts/" + set + "/" + posttype):
                    threadpath = _COREPATH + "/campaigns/" + campaignid + "/posts/" + set + "/" + posttype + '/' + threadname

                    if os.path.isfile(threadpath) and re.match('^\d+\.html$',threadname):
                        group = re.findall('^(\d+)\.html$',threadname)
                        if len(group) > 0:
                            roottreeid = group.pop()

                            htmlpath=_COREPATH + "/campaigns/" + campaignid + "/posts/" + set + "/" + posttype + "/"+roottreeid+".html"
                            templatehtmlpath= SCRIPTPATH + "/templates/posts/TEMPLATE-"+set+".html"
                            writefile = open(htmlpath, 'w')
                            if writefile:

                                print htmlpath
                                if os.path.exists(templatehtmlpath):
                                    with open(templatehtmlpath) as f:
                                        for line in f:
                                            strline = line
                                            if re.match(".*var NAME\s*=\s*['\"]INDEX[\"'];.*", line):
                                                strline = line.replace("INDEX",roottreeid)
                                            if set == 'static' and re.match(".*id=[\"']postdiv[\"'].*", line):
                                                writefile.write(strline)
                                                writeposts.fillStaticPostFile(campaignid,posttype,roottreeid,writefile,posttreedata,campaignuserdata,campaigncharacterdata)
                                            else:
                                                writefile.write(strline)
                                writefile.close()



for filename in os.listdir(_COREPATH+"/campaigns/"):
    if re.match('^\d+$',filename) and os.path.isdir(_COREPATH+"/campaigns/"+filename):
        campaignid=filename

        if 'campaignid' in runopts.keys():
            if campaignid not in runopts['campaignid']:
                continue

        campaignuserdata=loadusers.loadUserInfo(_COREPATH,campaignid,'users')
        campaigncharacterdata=loadusers.loadUserInfo(_COREPATH,campaignid,'characters')


        postsets=['dynamic', 'static']
        for set in postsets:

            posttreedata = loadposts.loadPostsFromCampaignData(campaignid)
            for posttype in posttypes:
                postlistdata = loadusers.loadUserListInfo(_COREPATH,campaignid,posttype)

                listpath = _COREPATH + "/campaigns/" + campaignid + "/_data/lists/"
                postsets=['dynamic', 'static']
                for set in postsets:
                    templatehtmlpath = SCRIPTPATH + "/templates/"+posttype+"-"+set+".html"
                    htmlpath = _COREPATH + "/campaigns/" + campaignid + "/" + posttype + "-"+set+"-list.html"

                    writefile = open(htmlpath, 'w')
                    if writefile:

                        print htmlpath
                        if os.path.exists(templatehtmlpath):
                            with open(templatehtmlpath) as f:
                                for line in f:
                                    strline = line
                                    if set == 'static' and re.match(".*id=[\"']postlistdiv[\"'].*", line):
                                        writefile.write(strline)
                                        writepostlist.fillStaticListFile(campaignid,posttype,writefile,posttreedata,campaignuserdata,campaigncharacterdata,postlistdata)
                                    else:
                                        writefile.write(strline)
                        writefile.close()

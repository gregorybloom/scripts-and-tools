import os,re,shutil,sys,imp

#  DB parsing script #7
#  pushes the templates
#       afterwords, use the campaign zipper to find and zip campaigns
#           - zipcampaign.sh


SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/config/herobuildconf.py')


_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT


posttypes=['xstorypost','xmessagepost']
for filename in os.listdir(_COREPATH+"/campaigns/"):
    if re.match('^\d+$',filename) and os.path.isdir(_COREPATH+"/campaigns/"+filename):
        campaignid=filename

        for posttype in posttypes:

            if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/" + posttype):
                os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/" + posttype)

            if os.path.exists(SCRIPTPATH + "/templates/_template"):
                templatefolderpath = _COREPATH + "/campaigns/" + campaignid + "/_template"
                if os.path.exists(templatefolderpath):
                    shutil.rmtree(templatefolderpath, ignore_errors=True)
                if not os.path.exists(templatefolderpath):
                    shutil.copytree(SCRIPTPATH + "/templates/_template", templatefolderpath)
            if os.path.exists(SCRIPTPATH + "/templates/posts/posttemplate"):
                templatefolderpath=_COREPATH + "/campaigns/" + campaignid + "/posts/" + posttype +"/posttemplate"
                if os.path.exists(templatefolderpath):
                    shutil.rmtree(templatefolderpath, ignore_errors=True)
                if not os.path.exists(templatefolderpath):
                    shutil.copytree(SCRIPTPATH + "/templates/posts/posttemplate", templatefolderpath)

            for threadname in os.listdir(_COREPATH + "/campaigns/" + campaignid + "/posts/" + posttype):
                threadpath = _COREPATH + "/campaigns/" + campaignid + "/posts/" + posttype + '/' + threadname

                if os.path.isfile(threadpath) and re.match('^\d+\.html$',threadname):
                    group = re.findall('^(\d+)\.html$',threadname)
                    if len(group) > 0:
                        roottreeid = group.pop()


                        htmlpath=_COREPATH + "/campaigns/" + campaignid + "/posts/" + posttype + "/"+roottreeid+".html"
                        templatehtmlpath= SCRIPTPATH + "/templates/posts/TEMPLATE.html"

                        writefile = open(htmlpath, 'w')
                        if writefile:

                            print htmlpath
                            if os.path.exists(templatehtmlpath):
                                with open(templatehtmlpath) as f:
                                    for line in f:
                                        strline = line
                                        if re.match(".*var NAME\s*=\s*['\"]INDEX[\"'];.*", line):
                                            strline = line.replace("INDEX",roottreeid)

                                        writefile.write(strline)
                            writefile.close()



            templatehtmlpath = SCRIPTPATH + "/templates/"+posttype+".html"
            htmlpath = _COREPATH + "/campaigns/" + campaignid + "/" + posttype + ".html"

            writefile = open(htmlpath, 'w')
            if writefile:
                print htmlpath
                if os.path.exists(templatehtmlpath):
                    with open(templatehtmlpath) as f:
                        for line in f:
                            strline = line
                            writefile.write(strline)
                writefile.close()

import re,os,json,sys,imp
#  DB parsing script #3
#  builds the temp files
#       use the output from this to build the patch file - see "infodump
#       afterwords, build the campaigns
#           - buildcampaigns.py



SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/config/herobuildconf.py')


_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT

if not os.path.exists(_COREPATH):
    os.makedirs(_COREPATH)

if not os.path.exists(_COREPATH+"/tabledump"):
    os.makedirs(_COREPATH+"/tabledump")
if not os.path.exists(_COREPATH+"/infodump"):
    os.makedirs(_COREPATH+"/infodump")




if not os.path.exists(_TMPPATH+"/tmp/users"):
    os.makedirs(_TMPPATH+"/tmp/users")
if not os.path.exists(_TMPPATH+"/tmp/campaigns"):
    os.makedirs(_TMPPATH+"/tmp/campaigns")
if not os.path.exists(_TMPPATH+"/tmp/characters"):
    os.makedirs(_TMPPATH+"/tmp/characters")
if not os.path.exists(_TMPPATH+"/tmp/quotes"):
    os.makedirs(_TMPPATH+"/tmp/quotes")
if not os.path.exists(_TMPPATH+"/tmp/timeline"):
    os.makedirs(_TMPPATH+"/tmp/timeline")


with open(_COREPATH+"/tabledump/xuser.txt", 'r') as f:
    for line in f:
        userdata = json.loads(line.rstrip())
        writefile = open(_TMPPATH + "/tmp/users/"+userdata['userid']+".txt", 'w')
        if writefile:
            writefile.write(line)
            writefile.close()

with open(_COREPATH+"/tabledump/xcampaign.txt", 'r') as f:
    for line in f:
        campaigndata = json.loads(line.rstrip())
        writefile = open(_TMPPATH + "/tmp/campaigns/"+campaigndata['campaignid']+".txt", 'w')
        if writefile:
            writefile.write(line)
            writefile.close()

with open(_COREPATH+"/tabledump/xcharacter.txt", 'r') as f:
    for line in f:
        characterdata = json.loads(line.rstrip())
        if not os.path.exists(_TMPPATH + "/tmp/characters/"+characterdata['campaignid']):
            os.makedirs(_TMPPATH + "/tmp/characters/"+characterdata['campaignid'])
        writefile = open(_TMPPATH + "/tmp/characters/"+characterdata['campaignid']+"/"+characterdata['userid']+".txt", 'w')
        if writefile:
            writefile.write(line)
            writefile.close()

with open(_COREPATH+"/tabledump/xquotes.txt", 'r') as f:
    for line in f:
        quotedata = json.loads(line.rstrip())
        if not os.path.exists(_TMPPATH + "/tmp/quotes/"+quotedata['campaignid']):
            os.makedirs(_TMPPATH + "/tmp/quotes/"+quotedata['campaignid'])
        writefile = open(_TMPPATH + "/tmp/quotes/"+quotedata['campaignid']+"/"+quotedata['\"position\"']+".txt", 'w')
        if writefile:
            writefile.write(line)
            writefile.close()

with open(_COREPATH+"/tabledump/xtimeline.txt", 'r') as f:
    for line in f:
        timelinedata = json.loads(line.rstrip())
        if not os.path.exists(_TMPPATH + "/tmp/timeline/"+timelinedata['campaignid']):
            os.makedirs(_TMPPATH + "/tmp/timeline/"+timelinedata['campaignid'])
        writefile = open(_TMPPATH + "/tmp/timeline/"+timelinedata['campaignid']+"/"+timelinedata['\"position\"']+".txt", 'w')
        if writefile:
            writefile.write(line)
            writefile.close()



'''
with open(_COREPATH+"/tabledump/xstorypost.txt", 'r') as f:
    for line in f:
        postdata = json.loads(line.rstrip())
        if not os.path.exists(_TMPPATH + "/tmp/posts/"+postdata['campaignid']):
            os.makedirs(_TMPPATH + "/tmp/posts/"+postdata['campaignid'])
        if not os.path.exists(_TMPPATH + "/tmp/posts/"+postdata['campaignid']+"/story/"):
            os.makedirs(_TMPPATH + "/tmp/posts/"+postdata['campaignid']+"/story/")

        writefile = open(_TMPPATH + "/tmp/posts/"+postdata['campaignid']+"/story/"+postdata['storypostid']+".txt", 'w')
        if writefile:
            writefile.write(line)
            writefile.close()


with open(_COREPATH+"/tabledump/xmessagepost.txt", 'r') as f:
    for line in f:
        postdata = json.loads(line.rstrip())
        if not os.path.exists(_TMPPATH + "/tmp/posts/"+postdata['campaignid']):
            os.makedirs(_TMPPATH + "/tmp/posts/"+postdata['campaignid'])
        if not os.path.exists(_TMPPATH + "/tmp/posts/"+postdata['campaignid']+"/msg/"):
            os.makedirs(_TMPPATH + "/tmp/posts/"+postdata['campaignid']+"/msg/")

        writefile = open(_TMPPATH + "/tmp/posts/"+postdata['campaignid']+"/msg/"+postdata['messagepostid']+".txt", 'w')
        if writefile:
            writefile.write(line)
            writefile.close()
'''

import re,os,json,sys,shutil,imp
import pprint

SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/config/herobuildconf.py')
_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT


def loadPostsFromCampaignData(campaignid):
    posttreedata = None

    posttypes=['xstorypost','xmessagepost']
    for posttype in posttypes:

        jsonstartpath = _COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/json/"
        if os.path.exists(jsonstartpath):
            for filename in os.listdir(jsonstartpath):
                if re.match("^\d+\.json$", filename):
                    rootid=re.findall("^(\d+)",filename).pop()
                    rootthreaddata=None
                    print 'loading: ',jsonstartpath+"/"+filename
                    with open(jsonstartpath+"/"+filename, 'r') as f:
                        for line in f:
                            rootthreaddata = json.loads(line.rstrip())
                    if rootthreaddata is not None:

                        if posttreedata is None:
                            posttreedata={}
                        if campaignid not in posttreedata.keys():
                            posttreedata[campaignid]={}
                        if posttype not in posttreedata[campaignid].keys():
                            posttreedata[campaignid][posttype]={}
                        if rootid not in posttreedata[campaignid][posttype].keys():
                            posttreedata[campaignid][posttype][rootid]=rootthreaddata
    return posttreedata

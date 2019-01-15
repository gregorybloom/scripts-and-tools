import re,os,json,sys,shutil,imp
import pprint

def loadUserInfo(corepath,campaignid,posttype):
    campaignuserdata={}
    listpath = corepath + "/campaigns/" + campaignid + "/_data/" + posttype + "/json/"
    if os.path.exists(listpath):
        for filename in os.listdir(listpath):
            if os.path.isfile(listpath+"/"+filename):
                with open(listpath+"/"+filename, 'r') as f:
                    for line in f:
                        tmpdata = json.loads(line.rstrip())
                        if 'userid' in tmpdata.keys():
                            campaignuserdata[tmpdata['userid']]=tmpdata
    return campaignuserdata


def loadUserListInfo(corepath,campaignid,posttype):
    campaignuserdata={}
    listpath = corepath + "/campaigns/" + campaignid + "/_data/lists/"
    if os.path.exists(listpath):
        filepath = listpath+"/json/"+posttype+"list.json"
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    campaignuserdata = json.loads(line.rstrip())
    return campaignuserdata

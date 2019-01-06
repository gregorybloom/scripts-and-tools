import re,os,json,sys,shutil,imp
from datetime import datetime
#  DB parsing script #1
#  parses the posts
#       afterwords, debug the tree!
#           - debugtree.py



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





def placePostData(postid,dict,postdata,reservelist,depth,fulldict):
    if 'parentid' not in postdata.keys():
        print "CRASH A"
        print postdata
        sys.exit(1)


    if postdata['parentid'] in dict.keys():

        if '_subposts' not in dict[postdata['parentid']].keys():
            dict[postdata['parentid']]['_subposts']={}

        if postid not in dict[postdata['parentid']]['_subposts'].keys():
            dict[postdata['parentid']]['_subposts'][postid]={}

            dict[postdata['parentid']]['_subposts'][postid]['_indexdata']={}
            dict[postdata['parentid']]['_subposts'][postid]['_indexdata']['postid']=postid
            dict[postdata['parentid']]['_subposts'][postid]['_indexdata']['parentid']=postdata['parentid']
            dict[postdata['parentid']]['_subposts'][postid]['_indexdata']['progenitorid']=postdata['progenitorid']
            dict[postdata['parentid']]['_subposts'][postid]['_indexdata']['campaignid']=postdata['campaignid']
            return 1
        else:
            print "CRASH B"
            print postdata,dict[postdata['parentid']]
            sys.exit(1)
    else:
        for key,val in dict.iteritems():
            if '_subposts' not in dict[key].keys():
                dict[key]['_subposts']={}

            placed=placePostData(postid,dict[key]['_subposts'],postdata,reservelist,depth+1,fulldict)
            if(placed == 1):
#                if 'storypostid' in postdata.keys() and postdata['storypostid'] == '12528':
#                    print key,depth,postdata
                return 1
    return 0


def addToPostData(tablename,postdict,postdata,reservelist,addanywhere=False):

    if postdata['campaignid'] not in postdict['posttree'].keys():
        postdict['posttree'][ postdata['campaignid'] ]={}
        postdict['posttree'][ postdata['campaignid'] ]["xstorypost"]={}
        postdict['posttree'][ postdata['campaignid'] ]["xmessagepost"]={}

    postid=postdata["storypostid"] if "storypostid" in postdata.keys() else None
    if postid is None:
        postid=postdata["messagepostid"] if "messagepostid" in postdata.keys() else None

    if re.match('\d+',postdata['parentid']) and re.match('\d+',postdata['progenitorid']):

        placed=placePostData(postid,postdict['posttree'][ postdata['campaignid'] ][tablename],postdata,reservelist,1,postdict['posttree'][ postdata['campaignid'] ][tablename])
#        print '   -',postid,placed,postdata['campaignid'],tablename,addanywhere
        if not addanywhere or placed == 1:
            return placed
        else:
            for campaignid,campaigntree in postdict['posttree'].iteritems():
                if tablename in postdict['posttree'][campaignid].keys():
                    if campaignid != postdata['campaignid']:
                        placed=placePostData(postid,postdict['posttree'][campaignid][tablename],postdata,reservelist,1,postdict['posttree'][campaignid][tablename])
                        if placed == 1:
                            print '          .-', postid, tablename, placed, ', campaignid: ', postdata['campaignid'], ' -> ', campaignid
                            return placed
    else:
        if postid not in postdict['posttree'][ postdata['campaignid'] ][tablename].keys():
#            if postid == '224145':
#                print "******B",postdata['campaignid'],tablename,postdata['progenitorid'],' - ',postid
#                print '         ',postdict['posttree'][postdata['campaignid']][tablename].keys()
#                print '         ',postdata
            postdict['posttree'][postdata['campaignid']][tablename][postid]={}
            postdict['posttree'][postdata['campaignid']][tablename][postid]['_postdata'] = {}
            postdict['posttree'][postdata['campaignid']][tablename][postid]['_subposts'] = {}

            postdict['posttree'][postdata['campaignid']][tablename][postid]['_indexdata'] = {}
        postdict['posttree'][postdata['campaignid']][tablename][postid]['_indexdata']['postid']=postid
        postdict['posttree'][postdata['campaignid']][tablename][postid]['_indexdata']['parentid']=postdata['parentid']
        postdict['posttree'][postdata['campaignid']][tablename][postid]['_indexdata']['progenitorid']=postdata['progenitorid']
        postdict['posttree'][postdata['campaignid']][tablename][postid]['_indexdata']['campaignid']=postdata['campaignid']

        return 1
    return 0

def addPostFromReserveList(campaignid, postid, postdata, treedata, depth):
    if postdata['parentid'] in treedata.keys():
        if '_subposts' not in treedata[postdata['parentid']].keys():
            treedata[postdata['parentid']]['_subposts'] = {}
        treedata[postdata['parentid']]['_subposts'][postid] = {}

        treedata[postdata['parentid']]['_subposts'][postid]['_indexdata'] = {}
        treedata[postdata['parentid']]['_subposts'][postid]['_indexdata']['postid'] = postid
        treedata[postdata['parentid']]['_subposts'][postid]['_indexdata']['parentid'] = postdata['parentid']
        treedata[postdata['parentid']]['_subposts'][postid]['_indexdata']['progenitorid'] = postdata['progenitorid']
        treedata[postdata['parentid']]['_subposts'][postid]['_indexdata']['campaignid'] = postdata['campaignid']

        return 1
    else:
        for key, item in treedata.iteritems():
            if '_subposts' in treedata[key].keys():
                placed = addPostFromReserveList(campaignid, postid, postdata, treedata[key]['_subposts'], depth+1)
                if placed == 1:
                    return placed
    return 0


def patchLoadedData(postdata,patchlist):
    posttype=None
    patchid=None
    if 'messagepostid' in postdata.keys():
        posttype='xmessagepost'
        patchid=postdata['messagepostid']
    if 'storypostid' in postdata.keys():
        posttype='xstorypost'
        patchid=postdata['storypostid']
    if posttype is not None and patchid is not None:
        if posttype in patchlist.keys():
            if patchid in patchlist[posttype].keys():
                print '    => ',patchid,patchlist[posttype][patchid],postdata
                for key,value in patchlist[posttype][patchid].iteritems():

                    if key == 'storypostid' or key == 'messagepostid':
                        continue
                    postdata[key] = value


postdict={}
postdict['posttree']={}
postdict['count']={}

reservelist={}

patchlist={}
posttypes=['xstorypost','xmessagepost']
for posttype in posttypes:
    patchlist[posttype]={}
if os.path.exists(_COREPATH + "/tabledump/patchtable.txt"):
    with open(_COREPATH + "/tabledump/patchtable.txt", 'r') as f:
        for line in f:
            patchdata = json.loads(line.rstrip())
            patchid = None
            patchtype = None
            if 'messagepostid' in patchdata.keys():
                patchid = patchdata['messagepostid']
                patchtype = 'xmessagepost'
            if 'storypostid' in patchdata.keys():
                patchid = patchdata['storypostid']
                patchtype = 'xstorypost'

            if patchid is not None:
                if patchid not in patchlist[patchtype].keys():
                    patchlist[patchtype][patchid]=patchdata
                else:
                    for key,val in patchdata.iteritems():
                        patchlist[patchtype][patchid][key]=val



posttypes=['xstorypost','xmessagepost']
for posttype in posttypes:
    with open(_COREPATH + "/tabledump/"+posttype+".txt", 'r') as f:
        for line in f:
            postdata = json.loads(line.rstrip())
            patchLoadedData(postdata,patchlist)

            postid = postdata["storypostid"] if "storypostid" in postdata.keys() else None
            if postid is None:
                postid = postdata["messagepostid"] if "messagepostid" in postdata.keys() else None

            if re.match('\d+', postdata['parentid']):
                continue
            placed=addToPostData(posttype,postdict,postdata,reservelist,False)





count=0
posttypes=['xstorypost','xmessagepost']
for posttype in posttypes:
    with open(_COREPATH + "/tabledump/"+posttype+".txt", 'r') as f:
        for line in f:
            postdata = json.loads(line.rstrip())
            patchLoadedData(postdata,patchlist)

            postid = postdata["storypostid"] if "storypostid" in postdata.keys() else None
            if postid is None:
                postid = postdata["messagepostid"] if "messagepostid" in postdata.keys() else None

            if not re.match('\d+', postdata['parentid']):
                continue

            count=count+1

            placed=addToPostData(posttype,postdict,postdata,reservelist,False)

            if(count%500==0):
                print count,postid,placed,postdata
#            if postid == '12528':
#                print '***',placed,postdata
#                print postdata['parentid']
#                print re.match("\""+postdata['parentid']+"\"\:",json.dumps(postdict))


            if placed==0:
                if postdata['campaignid'] not in reservelist.keys():
                    reservelist[postdata['campaignid']]={}
                if posttype not in reservelist[postdata['campaignid']].keys():
                    reservelist[postdata['campaignid']][posttype]={}

                reservelist[postdata['campaignid']][posttype][postid]=postdata


rcountmax=len(reservelist.keys())
rcount=0
for campaignid,list in reservelist.iteritems():
    rcount += 1
    for posttype,list2 in reservelist[campaignid].iteritems():

        leftovers=False
        rmax=300
        for repeat in range(0,rmax):
            if len(reservelist[campaignid][posttype].keys()) == 0:
                continue

            checkset=[]
            checkset.append( len(reservelist[campaignid][posttype].keys()) )
            print 'reservelist ',' start:',rcount,'/',rcountmax,',',leftovers,' - ',campaignid,posttype,repeat,',',len(reservelist[campaignid][posttype].keys()),datetime.now().strftime('%H:%M:%S')


            postlist=reservelist[campaignid][posttype].keys()
            for postid in postlist:
                postdata=reservelist[campaignid][posttype][postid]
                if postdata['campaignid'] in postdict['posttree'].keys():
                    if posttype in postdict['posttree'][postdata['campaignid']].keys():

                        if re.match('\d+',postdata['progenitorid']) and re.match('\d+',postdata['parentid']):

                            placed=addPostFromReserveList(campaignid,postid,postdata,postdict['posttree'][postdata['campaignid']][posttype],1)
                            if placed==1:
                                del reservelist[campaignid][posttype][postid]
                            else:
                                if leftovers == False:
                                    continue

                                for camp_id,camp_set in postdict['posttree'].iteritems():
                                    if posttype in postdict['posttree'][camp_id].keys():
                                        if camp_id != postdata['campaignid']:
                                            placed = addPostFromReserveList(camp_id, postid, postdata,postdict['posttree'][camp_id][posttype], 1)
#                                            if postid == '284834':
#                                                print '****',placed,camp_id,postid,posttype,postdata
#                                                sys.exit(1)

                                            if placed == 1:
                                                del reservelist[postdata['campaignid']][posttype][postid]
                                                print '          .--', postid, posttype, placed, ', campaignid: ', \
                                                postdata['campaignid'], ' -> ', camp_id
                                                break

                        else:
                            if postid not in postdict['posttree'][postdata['campaignid']].keys():
                                postdict['posttree'][postdata['campaignid']][postid]={}
                            else:
                                print "FUSDFKLSDF",postid,postdict['posttree'][postdata['campaignid']].keys()
                                print postdata
                                sys.exit(1)
                            if '_postdata' not in postdict['posttree'][postdata['campaignid']][postid].keys():
                                postdict['posttree'][postdata['campaignid']][postid]['_postdata']=postdata
                            if '_subposts' not in postdict['posttree'][postdata['campaignid']][postid].keys():
                                postdict['posttree'][postdata['campaignid']][postid]['_subposts']={}

                                postdict['posttree'][postdata['campaignid']][postid]['_indexdata']={}
                                postdict['posttree'][postdata['campaignid']][postid]['_indexdata']['postid'] = postid
                                postdict['posttree'][postdata['campaignid']][postid]['_indexdata']['parentid'] = postdata['parentid']
                                postdict['posttree'][postdata['campaignid']][postid]['_indexdata']['progenitorid'] = postdata['progenitorid']
                                postdict['posttree'][postdata['campaignid']][postid]['_indexdata']['campaignid'] = postdata['campaignid']

                else:
                    print "FSCK"
                    sys.exit(1)

            checkset.append( len(reservelist[campaignid][posttype].keys()) )
            print 'reservelist ',' final:',rcount,'/',rcountmax,',',leftovers,' - ',campaignid,posttype,repeat,',',len(reservelist[campaignid][posttype].keys())
            if checkset[0] == checkset[1]:
                if leftovers == False:
                    leftovers = True
                    continue

                print 'no fixes, move on'
                print campaignid,posttype,reservelist[campaignid][posttype].keys()
                break
            elif repeat==(rmax-1):
                print "Range Overload"




writefile = open(_COREPATH + "/infodump/posttree.txt", 'w')
if writefile:
    json.dump(postdict['posttree'], writefile)
    writefile.write("\n")
    writefile.close()

writefile = open(_COREPATH + "/infodump/postcounts.txt", 'w')
if writefile:
    json.dump(postdict['count'], writefile)
    writefile.write("\n")
    writefile.close()



if os.path.exists(_COREPATH + "/infodump/reservelist"):
    shutil.rmtree(_COREPATH + "/infodump/reservelist")
if not os.path.exists(_COREPATH + "/infodump/reservelist"):
    os.makedirs(_COREPATH + "/infodump/reservelist")
for campaignid,list in reservelist.iteritems():
    for posttype,list2 in reservelist[campaignid].iteritems():
        if len(reservelist[campaignid][posttype].keys()) > 0:
            if not os.path.exists(_COREPATH + "/infodump/reservelist/"+posttype):
                os.makedirs(_COREPATH + "/infodump/reservelist/"+posttype)
            writefile = open(_COREPATH + "/infodump/reservelist/"+posttype+"/"+campaignid+".txt", 'w')
            if writefile:
                for postid,postdata in reservelist[campaignid][posttype].iteritems():
                    json.dump(postdata,writefile)
                    writefile.write("\n")
                writefile.close()
            writefile = open(_COREPATH + "/infodump/reservelist/"+posttype+"/"+campaignid+".list.txt", 'w')
            if writefile:
                json.dump(reservelist[campaignid][posttype].keys(),writefile)
                writefile.write("\n")
                writefile.close()

#for campaignid in postdict['count'].keys():
#    for posttype in postdict['count'][campaignid].keys():
#        print 'postcount:',campaignid,posttype,postdict['count'][campaignid][posttype]

'''
for campaignid in postdict['posttree'].keys():
    for posttype,list in postdict['posttree'][campaignid].iteritems():
        dumptext=json.dumps(postdict['posttree'][campaignid][posttype])
        grabids=re.findall("\"(\d+)\"\:",dumptext)
        print 'subposts:',campaignid,posttype,len(grabids)

        if not os.path.exists(_COREPATH + "/infodump/sublist/" + posttype):
            os.makedirs(_COREPATH + "/infodump/sublist/" + posttype)
        writefile = open(_COREPATH + "/infodump/sublist/" + posttype + "/" + campaignid + ".list.txt", 'w')
        if writefile:
            json.dump(grabids, writefile)
            writefile.write("\n")
            writefile.close()
'''
for campaignid,list in reservelist.iteritems():
    for posttype,list2 in reservelist[campaignid].iteritems():
        print 'reserve:',campaignid,posttype,len(reservelist[campaignid][posttype].keys()),',',reservelist[campaignid][posttype].keys()


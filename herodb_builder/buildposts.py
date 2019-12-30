from datetime import datetime as dt
import re,os,json,sys,shutil,imp,time
import pprint



pp = pprint.PrettyPrinter(indent=4)

#  DB parsing script #6
#  builds the final posts
#       afterwords, push the templates
#           - pushtemplates.py


SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))
heroconf = imp.load_source('heroconf', SCRIPTPATH+'/../config/herobuildconf.py')


writeposts = imp.load_source('writeposts', SCRIPTPATH+'/libs/writeposts.py')
writepostlist = imp.load_source('writepostlist', SCRIPTPATH+'/libs/writepostlist.py')
loadusers = imp.load_source('loadusers', SCRIPTPATH+'/libs/loadusers.py')
loadposts = imp.load_source('loadposts', SCRIPTPATH+'/libs/loadposts.py')



_COREPATH=heroconf._HEROPARSINGOUTPUT
_TMPPATH=heroconf._HEROTMPOUTPUT








def buildDepthpad(depth):
    depthpadbase="   "
    depthpad=""
    for repeat in range(0,depth):
        depthpad+=depthpadbase
    if depth == 1:
        depthpad = "  * "
    return depthpad


def printPostTrees(campaignid,posttype,rootid,postkey,postnode,parentnode,depth):
    depthpad = buildDepthpad(depth)
    print depthpad,postkey,postnode['_indexdata']
    if '_indexdata' in postnode.keys():
        if '_subposts' in postnode.keys():
            for key in postnode['_subposts'].keys():
                node=postnode['_subposts'][key]
                printPostTrees(campaignid,posttype,rootid,key,node,postnode,depth+1)


def dumpMissingIntoList(postid,subtree,postdata,posttype,misslist):
    for missingpostkey, missingpostgroup in misslist[postdata['campaignid']][posttype].iteritems():
        if '_chains' in misslist[postdata['campaignid']][posttype][missingpostkey].keys():
            for missingrootkey,missingrootpost in misslist[postdata['campaignid']][posttype][missingpostkey]['_chains'].iteritems():
                subtreeMissing = misslist[postdata['campaignid']][posttype][missingpostkey]['_chains'][missingrootkey]
                placedMissing = addPostData(postid, missingrootkey, subtreeMissing, postdata, 0)
                if placedMissing == 1:
                    return 1
    return 0


def verifyPostTrees(campaignid,posttype,rootid,postkey,postnode,parentnode,misplacedlist,depth):
    depthpad = buildDepthpad(depth)
    if '_indexdata' in postnode.keys():
        if rootid == postnode['_indexdata']['postid'] or rootid == postnode['_indexdata']['progenitorid']:
            if '_subposts' in postnode.keys():
                for key in postnode['_subposts'].keys():
                    node=postnode['_subposts'][key]
                    verify=verifyPostTrees(campaignid,posttype,rootid,key,node,postnode,misplacedlist,depth+1)
                    if verify is not None:
                        return verify
        else:
            if campaignid not in misplacedlist.keys():
                misplacedlist[campaignid]={}
            if posttype not in misplacedlist[campaignid].keys():
                misplacedlist[campaignid][posttype]={}


            lostkey=rootid+"-"+postnode['_indexdata']['progenitorid']
            if lostkey not in misplacedlist[campaignid][posttype].keys():
                misplacedlist[campaignid][posttype][lostkey]={}
                misplacedlist[campaignid][posttype][lostkey]['_chains']={}

            print depthpad,'  - relocated thread: ',campaignid,posttype,lostkey,'->',postkey, '  : ',rootid,postnode['_indexdata']
            misplacedlist[campaignid][posttype][lostkey]['_chains'][postkey]=parentnode['_subposts'].pop(postkey,None)
    else:
        print "FUSCKSF"
        print rootid,postkey,parentnode['_indexdata']
        print postnode.keys()
        print parentnode.keys()
        sys.exit(1)


def buildChecklist(campaignid,node, checklistnode):
#    if campaignid == '17313':
#        print node['_indexdata']

    if '_subposts' in node.keys():
        for nodeid, nodeval in node['_subposts'].iteritems():
#            if nodeid == '230319':
#                print '****',nodeid,nodeval
#                print '           from: ',node['_indexdata']

            checklistnode[nodeid] = 1;
            buildChecklist(campaignid,node['_subposts'][nodeid], checklistnode)


def printSubThread(campaignid,posttype,roottreeid,subtree):
    if re.match("^\\*N$",campaignid):
        campaignid='N'

    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/")
    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/")

    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/json"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/json")
    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/js"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/js")


    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/posttemplate/js"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/posttemplate/js")
    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/posttemplate/css"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype + "/posttemplate/css")

    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/posttemplate/js"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/posttemplate/js")
    if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/posttemplate/css"):
        os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/posttemplate/css")


    jsonpath = _COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/json/" + roottreeid + ".json"
    writefile = open(jsonpath, 'w')
    if writefile:
        json.dump(subtree, writefile)
        writefile.close()

    jsonpath = _COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/js/" + roottreeid + ".js"
    writefile = open(jsonpath, 'w')
    if writefile:
        stringdata = 'var JSONDATA = '+json.dumps(subtree)+';'
        writefile.write(stringdata)
        writefile.close()





def addPostData(postid, curnodeid, subtree, postdata, depth):
#    if curnodeid == '230191':
#        print 'xxx',postid, curnodeid, subtree['_indexdata']
#    if postid == '230191':
#        print 'xx-',postid, curnodeid, subtree['_indexdata']

    if curnodeid == postid:
        if '_postdata' in subtree.iteritems():
            del subtree['_postdata']
        subtree['_postdata'] = postdata
#        if depth == 0:
#            print 'root node added!', curnodeid, postdata
        return 1

    if '_subposts' in subtree.keys():
        if postid in subtree['_subposts'].keys():
            placed = addPostData(postid, postid, subtree['_subposts'][postid], postdata, (depth+1))
            if placed == 1:
                return 1
            else:
                print "WTF"
                sys.exit(1)
        else:
            for nodeid, nodetree in subtree['_subposts'].iteritems():
                placed = addPostData(postid, nodeid, nodetree, postdata, (depth+1))
                if placed == 1:
                    return 1
    return 0



def CheckChecklist(postid,posttype,isroot,postdata,checklist,missingtype=False):

    if postdata['campaignid'] not in checklist.keys():
        return False
    if posttype not in checklist[postdata['campaignid']].keys():
        return False

    if not missingtype:
#        if postid == '14156':
#            print 'xA', isroot,postdata['progenitorid'],checklist[postdata['campaignid']][posttype].keys()


        if isroot and postid not in checklist[postdata['campaignid']][posttype].keys():
            return False
        if not isroot and postdata['progenitorid'] not in checklist[postdata['campaignid']][posttype].keys():
            return False
        if not isroot and postid not in checklist[postdata['campaignid']][posttype][postdata['progenitorid']].keys():
            return False
        return True
    else:
        if postid in checklist[postdata['campaignid']][posttype].keys():
            return True
        for rootcheckid,rootset in checklist[postdata['campaignid']][posttype].iteritems():
            if postid in checklist[postdata['campaignid']][posttype][rootcheckid].keys():
                return True
        return False


def CheckTreeRoot(postid,campaignid,posttype,isroot,postdata,treedata,missingtype=False):
    if re.match("^\\*N$",campaignid):
        campaignid='N'

    if not missingtype:

        if isroot and postid not in treedata[postdata['campaignid']][posttype].keys():
            return False
        if not isroot and postdata['progenitorid'] not in treedata[postdata['campaignid']][posttype].keys():
            return False
        return True
    else:
        if campaignid in treedata.keys():
            if posttype in treedata[campaignid].keys():
                for lostkey, lostgroup in treedata[campaignid][posttype].iteritems():
                    if '_chains' in treedata[campaignid][posttype][lostkey].keys():
                        if postid in treedata[campaignid][posttype][lostkey]['_chains'].keys():
                            return True
                        else:

#                            if postid == '14156':
#                                print 'xxx', isroot, postdata['progenitorid'], treedata[postdata['campaignid']][posttype].keys()

                            def checkTreeBody(postid,previd,postdata,treenode,depth):
                                depthpad = buildDepthpad(depth)
                                if '_subposts' in treenode.keys():
                                    if postid in treenode['_subposts'].keys():
                                        return True
                                    else:
                                        for subkey,subnode in treenode['_subposts'].iteritems():
                                            subcheck = checkTreeBody(postid,subkey,postdata,subnode,depth)
                                            if subcheck:
                                                return True
                                return False

                            for rootkey,rootnode in treedata[campaignid][posttype][lostkey]['_chains'].iteritems():
                                check = checkTreeBody(postid,rootkey,postdata,rootnode,1)
                                if check:
                                    return True
        return False



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
#                print '    => ',patchid,patchlist[posttype][patchid],postdata
                for key,value in patchlist[posttype][patchid].iteritems():
                    if key == 'storypostid' or key == 'messagepostid':
                        continue
                    postdata[key] = value


def addRootThread(campaignid,posttype,rootid,rootnode,threadlist):
    if re.match("^\\*N$",campaignid):
        campaignid='N'
    if campaignid not in threadlist.keys():
        threadlist[campaignid]={}
    if posttype not in threadlist[campaignid].keys():
        threadlist[campaignid][posttype]={}
    threadlist[campaignid][posttype][rootid]={}
    threadlist[campaignid][posttype][rootid]['postid']=rootid;
    threadlist[campaignid][posttype][rootid]['postdate']=rootnode['_postdata']['postdate'];
    threadlist[campaignid][posttype][rootid]['posttitle']=rootnode['_postdata']['posttitle'];
    threadlist[campaignid][posttype][rootid]['userid']=rootnode['_postdata']['userid'];






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



rootthreads={}
posttreedata=None

if 'campaignid' not in runopts.keys():
    print 'loading post tree'
    with open(_COREPATH+"/infodump/posttree.txt", 'r') as f:
        for line in f:
            posttreedata = json.loads(line.rstrip())
else:
    campaignidlist = runopts['campaignid']
    for campaignid in campaignidlist:
        if posttreedata is None:
            posttreedata={}

        posttreeitem = loadposts.loadPostsFromCampaignData(campaignid)
        if posttreeitem is not None:
            posttreedata[campaignid] = posttreeitem[campaignid]


rootthreadlist={}
patchlist={}
posttypes=['xstorypost','xmessagepost']
for posttype in posttypes:
    patchlist[posttype]={}
if os.path.exists(_COREPATH + "/tabledump/patchtable.txt"):
    with open(_COREPATH + "/tabledump/patchtable.txt", 'r') as f:
        for line in f:
            patchdata = json.loads(line.rstrip())
            if 'messagepostid' in patchdata.keys():
                patchlist['xmessagepost'][patchdata['messagepostid']]=patchdata
            if 'storypostid' in patchdata.keys():
                patchlist['xstorypost'][patchdata['storypostid']]=patchdata





misplacedlist={}
posttypes=['xstorypost','xmessagepost']
for campaignid, postset in posttreedata.iteritems():
    if re.match("^\\*N$",campaignid):
        campaignid='N'

    for posttype in posttypes:
        if posttype in posttreedata[campaignid].keys():

#            if campaignid == '17313':
#                print 'v',campaignid,posttype,posttreedata[campaignid][posttype].keys()
            for rootid,rootnode in posttreedata[campaignid][posttype].iteritems():
#                if rootid == '22' or rootid == '12483':
#                    pp.pprint(rootnode)
                verifyPostTrees(campaignid,posttype,rootid,rootid,rootnode,None,misplacedlist,1)


    ###  BUILD THREAD CHECKLIST
    postchecklist = {}
    for campaignid,postset in posttreedata.iteritems():
        if re.match("^\\*N$",campaignid):
            campaignid='N'

        if len(postset['xstorypost'].keys()) > 0 or len(postset['xmessagepost'].keys()) > 0:
            for posttype,rootlist in posttreedata[campaignid].iteritems():

                if campaignid not in postchecklist.keys():
                    postchecklist[campaignid] = {};
                if posttype not in postchecklist[campaignid].keys():
                    postchecklist[campaignid][posttype] = {};

                for rootid,rootnode in posttreedata[campaignid][posttype].iteritems():
                    postchecklist[campaignid][posttype][rootid]={};
                    postchecklist[campaignid][posttype][rootid]['_self']=1;

                    buildChecklist(campaignid,posttreedata[campaignid][posttype][rootid],postchecklist[campaignid][posttype][rootid])


misplacedChecklist = {}
for campaignid,postset1 in misplacedlist.iteritems():
    if re.match("^\\*N$",campaignid):
        campaignid='N'

    for posttype,postset2 in misplacedlist[campaignid].iteritems():
        if campaignid not in misplacedChecklist.keys():
            misplacedChecklist[campaignid] = {};
        if posttype not in misplacedChecklist[campaignid].keys():
            misplacedChecklist[campaignid][posttype] = {};

        for lostkey,postset3 in misplacedlist[campaignid][posttype].iteritems():
            if '_chains' in misplacedlist[campaignid][posttype][lostkey].keys():
                for postkey,posthead in misplacedlist[campaignid][posttype][lostkey]['_chains'].iteritems():
                    postid=misplacedlist[campaignid][posttype][lostkey]['_chains'][postkey]['_indexdata']['postid']

                    misplacedChecklist[campaignid][posttype][postid] = {};
                    misplacedChecklist[campaignid][posttype][postid]['_self'] = 1;

                    buildChecklist(campaignid,misplacedlist[campaignid][posttype][lostkey]['_chains'][postkey],misplacedChecklist[campaignid][posttype][postid])

                    if campaignid == '216540':
                        printPostTrees(campaignid, posttype, postkey, postkey, posthead, None, 1)


reserveindex={}
posttypes=['xstorypost','xmessagepost']
for campaignid, postset in posttreedata.iteritems():
    if re.match("^\\*N$",campaignid):
        campaignid='N'

    for posttype in posttypes:

        filepath=_COREPATH + "/infodump/reservelist/"+posttype+"/"+campaignid+".list.txt"
        if os.path.exists(filepath):
            reserveindex[campaignid]={}
            with open(filepath, 'r') as f:
                for line in f:
                    if re.match("^\[.*\]",line):
                        reserveindex[campaignid][posttype] = json.loads(line.rstrip())

'''
print reserveindex.keys()
for campaignid,list in reserveindex.iteritems():
    for posttype,list2 in reserveindex[campaignid].iteritems():
        print campaignid,posttype,len(reserveindex[campaignid][posttype]),reserveindex[campaignid][posttype]
'''
'''
for lostkey,lostgroup in misplacedlist['17313']['xstorypost'].iteritems():
    if '_chains' in misplacedlist['17313']['xstorypost'][lostkey].keys():
        if '12516' in misplacedlist['17313']['xstorypost'][lostkey]['_chains'].keys():
            pp.pprint(misplacedlist['17313']['xstorypost'][lostkey]['_chains']['12516'])
sys.exit(1)
'''


#for rootid,group in misplacedChecklist['17313']['xstorypost'].iteritems():
#    print '17313','xstorypost',rootid,group
#for key,node in misplacedchecklist.iteritems():
#    print key,node


count=0
posttypes=['xstorypost','xmessagepost']
for posttype in posttypes:
    with open(_COREPATH + "/tabledump/"+posttype+".txt", 'r') as f:
        for line in f:
            postdata = json.loads(line.rstrip())
            if re.match("^\\*N$",postdata['campaignid']):
                postdata['campaignid']='N'

            patchLoadedData(postdata,patchlist)


            if 'campaignid' in runopts.keys():
                if postdata['campaignid'] != runopts['campaignid']:
                    continue


            if postdata['campaignid'] in posttreedata.keys():
                if posttype in posttreedata[postdata['campaignid']].keys():

                    isroot=True
                    if re.match('\d+', postdata['parentid']) and re.match('\d+', postdata['progenitorid']):
                        isroot=False
                    postid = postdata["storypostid"] if "storypostid" in postdata.keys() else None
                    if postid is None:
                        postid = postdata["messagepostid"] if "messagepostid" in postdata.keys() else None


                    if postdata['campaignid'] in reserveindex.keys():
                        if posttype in reserveindex[postdata['campaignid']].keys():
                            if postid in reserveindex[postdata['campaignid']][posttype]:
                                print 'reserve postdata - skipped:',postdata['campaignid'],posttype,postid
                                continue


                    check=CheckChecklist(postid,posttype,isroot,postdata,postchecklist)
                    if check is False:
                        check = CheckChecklist(postid, posttype,isroot,postdata, misplacedChecklist,True)
                    if check is False:
                        print
                        print "FUCK a"
                        print postdata
                        print postdata['campaignid'], posttype, 'progid:', postdata['progenitorid'], ', parentid:', \
                        postdata['parentid']
                        print
                        if postdata['progenitorid'] in postchecklist[postdata['campaignid']][posttype].keys():
                            print ',',postchecklist[postdata['campaignid']][posttype][postdata['progenitorid']].keys()
                        else:
                            print 'x',postdata['progenitorid'],postchecklist[postdata['campaignid']][posttype].keys()
                        print postchecklist[postdata['campaignid']][posttype]
                        print
                        if postdata['progenitorid'] in postchecklist[postdata['campaignid']][posttype].keys():
                            print ',',postid, sorted(postchecklist[postdata['campaignid']][posttype][postdata['progenitorid']].keys())
                        else:
                            print 'x',postid,postdata['progenitorid'],sorted(postchecklist[postdata['campaignid']][posttype].keys())
                        sys.exit(1)

                    '''
                    check=CheckTreeRoot(postid,postdata['campaignid'],posttype,isroot,postdata,posttreedata)
                    if check is False:
                        check = CheckTreeRoot(postid,postdata['campaignid'],posttype,isroot,postdata,misplacedlist,True)
                    if check is False:
                        print
                        print "FUCK b"
                        print postdata
                        print postdata['campaignid'], posttype, 'progid:', postdata['progenitorid'], ', parentid:', postdata['parentid']
                        print postchecklist[postdata['campaignid']][posttype][postdata['progenitorid']].keys()
                        print postchecklist[postdata['campaignid']][posttype]
                        print
                        for lostkey, lostgroup in misplacedlist[postdata['campaignid']][posttype].iteritems():
                            if '_chains' in misplacedlist[postdata['campaignid']][posttype][lostkey].keys():
                                print postdata['campaignid'],posttype,lostkey,misplacedlist[postdata['campaignid']][posttype][lostkey]['_chains'].keys()
                                for rootkey, rootnode in misplacedlist[postdata['campaignid']][posttype][lostkey]['_chains'].iteritems():
                                    printPostTrees(postdata['campaignid'], posttype, rootkey, rootkey, rootnode, None, 1)

                        print
                        print postid, sorted(postchecklist[postdata['campaignid']][posttype][postdata['progenitorid']].keys())
                        print
                        sys.exit(1)
                    '''

                    roottreeid=postid
                    if not isroot:
                        roottreeid=postdata['progenitorid']

                    placed = 0
                    count = count+1
                    if roottreeid in posttreedata[postdata['campaignid']][posttype].keys():
                        subtree = posttreedata[postdata['campaignid']][posttype][roottreeid]
                        placed = addPostData(postid, roottreeid, subtree, postdata, 0)

                    if count%5000 == 0:
                        print '  - placing:', postdata['campaignid'], posttype, roottreeid, placed


                    if placed == 1:
                        if isroot:
                            del postchecklist[postdata['campaignid']][posttype][roottreeid]['_self']
                        else:
                            del postchecklist[postdata['campaignid']][posttype][roottreeid][postid]

                        if len(postchecklist[postdata['campaignid']][posttype][roottreeid].keys()) == 0:
#                            pp.pprint(posttreedata[postdata['campaignid']][posttype][roottreeid])


                            printSubThread(postdata['campaignid'],posttype,roottreeid,subtree)
#                            savedpostcount = len(re.findall("\"(postcontent)\"\:", json.dumps(subtree)))
#######################                                rootthreads[roottreeid]=posttreedata[postdata['campaignid']][posttype][roottreeid]['_postdata']
                            del posttreedata[postdata['campaignid']][posttype][roottreeid]
                            posttreedata[postdata['campaignid']][posttype][roottreeid] = 1
                            addRootThread(postdata['campaignid'], posttype, roottreeid, subtree, rootthreadlist)
                            jsonpath = _COREPATH + "/campaigns/" + postdata['campaignid'] + "/posts/dynamic/" + posttype + "/postdata/json/" + roottreeid + ".json"
                            print '-',jsonpath
#                                sys.exit(1)

                    else:
                        print "PLACEMENT FAILURE!"
                        print postid, roottreeid, subtree.keys()
                        print postdata
                        sys.exit(1)
                        '''
                        placedMissing = dumpMissingIntoList(postid, subtree, postdata, posttype, misplacedlist)
                        if placedMissing == 1:
                            if postid in misplacedChecklist[postdata['campaignid']][posttype].keys():
                                del misplacedChecklist[postdata['campaignid']][posttype][postid]['_self']
                            else:
                                clearedCheck = False
                                for rootchecktreeid,rootchecktree in misplacedChecklist[postdata['campaignid']][posttype].iteritems():
                                    if postid in misplacedChecklist[postdata['campaignid']][posttype][rootchecktreeid].keys():
                                        del misplacedChecklist[postdata['campaignid']][posttype][rootchecktreeid][postid]
                                        clearedCheck = True
                                        break
                                if clearedCheck == False:
                                    print "NO DROP!"
                                    print postdata
                                    for rootchecktreeid, rootchecktree in misplacedChecklist[postdata['campaignid']][posttype].iteritems():
                                        print '-',postdata['campaignid'],posttype,rootchecktreeid,rootchecktree
                                    sys.exit(1)


                        #                            lsdjflsjkdf
                        else:
                            #                            lsdjflsjkdf
                            print "PLACEMENT FAILURE!"
                            print postid,roottreeid,subtree.keys()
                            print postdata
                            sys.exit(1)
'''


            else:
                print postdata['campaignid'],posttreedata.keys()
                print "FAILURE"
                sys.exit(1)


        #        campaignpath = _COREPATH + "/campaigns/" + campaignid

        #            for rootid,roottree in rootlist.iteritems():


#                print campaignid,posttype,rootid,roottree

#        postdata = fetchPostData(posttype, campaignid, rootid)

print '======================='
for campaignid,camplist in postchecklist.iteritems():
    for posttype,postlist in postchecklist[campaignid].iteritems():
        for rootchecktreeid, rootchecktree in postchecklist[campaignid][posttype].iteritems():
            if len(postchecklist[campaignid][posttype][rootchecktreeid].keys()) > 0:
                print campaignid,posttype,rootchecktreeid,len(postchecklist[campaignid][posttype][rootchecktreeid].keys()),postchecklist[campaignid][posttype][rootchecktreeid].keys()


print '======================='

for campaignid,posttree in posttreedata.iteritems():
    if re.match("^\\*N$",campaignid):
        campaignid='N'

    campaignuserdata=loadusers.loadUserInfo(_COREPATH,campaignid,'users')
    campaigncharacterdata=loadusers.loadUserInfo(_COREPATH,campaignid,'characters')

    for posttype,postlist in posttreedata[campaignid].iteritems():

        if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype):
            os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/static/" + posttype)
        if not os.path.exists(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype):
            os.makedirs(_COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype)


        if os.path.exists(SCRIPTPATH + "/templates/_template"):
            templatefolderpath=_COREPATH + "/campaigns/" + campaignid + "/_template"
            if os.path.exists(templatefolderpath):
                shutil.rmtree(templatefolderpath, ignore_errors=True)
            if not os.path.exists(templatefolderpath):
                shutil.copytree(SCRIPTPATH + "/templates/_template", templatefolderpath)

        postsets=['dynamic', 'static']
        for set in postsets:
            if os.path.exists(SCRIPTPATH + "/templates/posts/posttemplate"):
                templatefolderpath=_COREPATH + "/campaigns/" + campaignid + "/posts/"+set+"/" + posttype +"/posttemplate"
                if os.path.exists(templatefolderpath):
                    shutil.rmtree(templatefolderpath, ignore_errors=True)
                if not os.path.exists(templatefolderpath):
                    shutil.copytree(SCRIPTPATH + "/templates/posts/posttemplate", templatefolderpath)


        for roottreeid,rootlist in posttreedata[campaignid][posttype].iteritems():
            if rootlist != 1:
                print "MISSING POST"
                print campaignid,posttype,roottreeid,rootlist
                sys.exit(1)


            postsets=['dynamic', 'static']
            for set in postsets:
                htmlpath=_COREPATH + "/campaigns/" + campaignid + "/posts/"+set+"/" + posttype + "/"+roottreeid+".html"
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


print '======================='

for campaignid,posttree in rootthreadlist.iteritems():
    if re.match("^\\*N$",campaignid):
        campaignid='N'

    campaignuserdata=loadusers.loadUserInfo(_COREPATH,campaignid,'users')
    campaigncharacterdata=loadusers.loadUserInfo(_COREPATH,campaignid,'characters')

    for posttype,postlist in rootthreadlist[campaignid].iteritems():

        listpath = _COREPATH + "/campaigns/" + campaignid + "/_data/lists/"
        if not os.path.exists(listpath+"/json"):
            os.makedirs(listpath+"/json")
        if not os.path.exists(listpath+"/js"):
            os.makedirs(listpath+"/js")

        writefile = open(listpath+"/json/"+posttype+"list.json", 'w')
        if writefile:
            json.dump(rootthreadlist[campaignid][posttype], writefile)
            writefile.close()

        writefile = open(listpath+"/js/"+posttype+"list.js", 'w')
        if writefile:
            stringdata = 'var JSONDATA_' +posttype.upper()+ ' = ' + json.dumps(rootthreadlist[campaignid][posttype]) + ';'
            writefile.write(stringdata)
            writefile.close()


        postsets=['dynamic', 'static']
        for set in postsets:
            templatehtmlpath = SCRIPTPATH + "/templates/"+posttype+"-"+set+".html"
            htmlpath = _COREPATH + "/campaigns/" + campaignid + "/" + posttype + "-"+set+"-list.html"
            writefile = open(htmlpath, 'w')
            if writefile:

                if os.path.exists(templatehtmlpath):
                    print htmlpath
                    with open(templatehtmlpath) as f:
                        for line in f:
                            strline = line
                            if set == 'static' and re.match(".*id=[\"']postlistdiv[\"'].*", line):
                                writefile.write(strline)
                                writepostlist.fillStaticListFile(campaignid,posttype,writefile,posttreedata,campaignuserdata,campaigncharacterdata,rootthreadlist[campaignid][posttype])
                            else:
                                writefile.write(strline)
                writefile.close()
    #        if campaignid == "235241":
    #            sys.exit(1)

        '''
    ####################### rebuild all of this as a php library function so both buildposts.py and pushtemplates.py can call it
        if campaignid in posttreedata.keys():
            if posttype in posttreedata[campaignid].keys():
                for roottreeid,rootlist in posttreedata[campaignid][posttype].iteritems():
                    html = _COREPATH + "/campaigns/" + campaignid + "/posts/dynamic/" + posttype + "/postdata/json/" + roottreeid + ".json"
        '''

import re,os,json,sys,shutil,imp
from datetime import datetime
#  DB parsing script #2
#  tests the post tree and looks for bugs
#       afterwords, build the temp files!
#           - buildtmps.py



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

        return 1
    return 0



def addFixToList(fixlist,fixtype,postid,postnode,fixobj):
    if fixtype not in fixlist.keys():
        fixlist[fixtype]={}
    if postid not in fixlist[fixtype].keys():
        fixlist[fixtype][postid]={}
        fixlist[fixtype][postid]['post']=json.loads(json.dumps(postnode))
        fixlist[fixtype][postid]['fix']=json.loads(json.dumps(fixobj))
    else:
        for key,val in fixobj.iteritems():
            fixlist[fixtype][postid]['fix'][key]=val


def verifyTreeNodes(campaignid,posttype,progenitorid,parentid,parentnode,posttree,fixlist,depth):

    if '_subposts' not in parentnode.keys():
        return

    for nodeid,postnode in parentnode['_subposts'].iteritems():
        if depth > 1 and postnode['_indexdata']['progenitorid'] != progenitorid:
            addFixToList(fixlist,posttype,nodeid,postnode['_indexdata'],{'progenitorid':progenitorid})


        if 'campaignid' in postnode.keys() and postnode['_indexdata']['campaignid'] != campaignid:
            addFixToList(fixlist,posttype,nodeid,postnode,{'campaignid':campaignid})

    for nodeid,postnode in parentnode['_subposts'].iteritems():
        verifyTreeNodes(campaignid,posttype,progenitorid,nodeid,postnode,posttree,fixlist,(depth+1))


fixlist={}

posttypes=['xstorypost','xmessagepost']

posttreedata=None
with open(_COREPATH+"/infodump/posttree.txt", 'r') as f:
    for line in f:
        posttreedata = json.loads(line.rstrip())


if posttreedata is not None:

    for campaignid, postset in posttreedata.iteritems():
        for posttype, rootlist in posttreedata[campaignid].iteritems():
            for rootid, rootnode in posttreedata[campaignid][posttype].iteritems():

                verifyTreeNodes(campaignid,posttype,rootid,rootid,rootnode,rootnode,fixlist,1)

for posttype,postset in fixlist.iteritems():
    for postid,data in fixlist[posttype].iteritems():

        fixset = fixlist[posttype][postid]['fix']
        postset = fixlist[posttype][postid]['post']

        print postid,' for ',posttype,postset,' = ',fixset





'''
array=( 225525 206905 215058 229661 195136 195157 261084 160024 403939 403931 403929 336792 336790 336800 336796 403938 403930 425403 397136 403935 403910 336812 336754 336753 403933 403926 351064 403937 423528 351023 336793 351018 351033 351034 351024 351021 336788 9226 17163 1129 403946 422218 422217 351025 110761 336821 519970 128501 1166006 347781 336327 336255 423526 351027 1036473 275200 336802 351022 351020 351004 351014 336757 403948 519974 351002 351030 351026 403934 336767 336814 336822 336823 336824 336813 336815 336760 336758 351029 336817 230319 262784 );


for id in "${array[@]}"; do
    childline=$(grep -irP "postid.\:\s+.\b"$id"\b" xstorypost.txt);
    childid=$(echo "$childline" | grep -oP "(?<=postid.\:\s.)\d+");
    parentid=$(echo "$childline" | grep -oP "(?<=parentid.\:\s.)\d+");
    parentline=$(grep -irP "postid.\:\s+.\b"$parentid"\b" xstorypost.txt);
    parentcamp=$(echo "$parentline" | grep -oP "(?<=campaignid.\:\s.)\d+");
    childcamp=$(echo "$childline" | grep -oP "(?<=campaignid.\:\s.)\d+");
    parentprog=$(echo "$parentline" | grep -oP "(?<=progenitorid.\:\s.)\d+");
    childprog=$(echo "$childline" | grep -oP "(?<=progenitorid.\:\s.)\d+");
    echostr="$childid  ->  ";
    if [[ ! "${array[@]}" =~ " ${parentid} " ]]; then
      echostr+="$parentid  , ";
      if [[ ! "$parentcamp" == "$childcamp" ]]; then
        echostr+="campaignid:  $childcamp  ->  $parentcamp  , ";
      fi;
      if [[ ! "$parentprog" == "$childprog" ]]; then
        echostr+="progenitorid:  $childprog  ->  $parentprog  , ";
      fi;
      echo "$echostr";
    else
      echostr+="$parentid<skip>";
      echo "$echostr";
    fi;
done


array=( 225525 206905 215058 229661 195136 195157 261084 160024 403939 403931 403929 336792 336790 336800 336796 403938 403930 425403 397136 403935 403910 336812 336754 336753 403933 403926 351064 403937 423528 351023 336793 351018 351033 351034 351024 351021 336788 9226 17163 1129 403946 422218 422217 351025 110761 336821 519970 128501 1166006 347781 336327 336255 423526 351027 1036473 275200 336802 351022 351020 351004 351014 336757 403948 519974 351002 351030 351026 403934 336767 336814 336822 336823 336824 336813 336815 336760 336758 351029 336817 230319 262784 ); for id in "${array[@]}"; do childline=$(grep -irP "postid.\:\s+.\b"$id"\b" xstorypost.txt); childid=$(echo "$childline" | grep -oP "(?<=postid.\:\s.)\d+"); parentid=$(echo "$childline" | grep -oP "(?<=parentid.\:\s.)\d+"); parentline=$(grep -irP "postid.\:\s+.\b"$parentid"\b" xstorypost.txt); parentcamp=$(echo "$parentline" | grep -oP "(?<=campaignid.\:\s.)\d+"); childcamp=$(echo "$childline" | grep -oP "(?<=campaignid.\:\s.)\d+"); parentprog=$(echo "$parentline" | grep -oP "(?<=progenitorid.\:\s.)\d+"); childprog=$(echo "$childline" | grep -oP "(?<=progenitorid.\:\s.)\d+"); echostr="$childid -> "; if [[ ! "${array[@]}" =~ " ${parentid} " ]]; then echostr+="$parentid , "; if [[ ! "$parentcamp" == "$childcamp" ]]; then echostr+="campaignid: $childcamp -> $parentcamp , "; fi; if [[ ! "$parentprog" == "$childprog" ]]; then echostr+="progenitorid: $childprog -> $parentprog , "; fi; echo "$echostr"; else echostr+="$parentid<skip>"; echo "$echostr"; fi;done


array=( 225525 206905 215058 229661 195136 195157 261084 160024 403939 403931 403929 336792 336790 336800 336796 403938 403930 425403 397136 403935 403910 336812 336754 336753 403933 403926 351064 403937 423528 351023 336793 351018 351033 351034 351024 351021 336788 9226 17163 1129 403946 422218 422217 351025 110761 336821 519970 128501 1166006 347781 336327 336255 423526 351027 1036473 275200 336802 351022 351020 351004 351014 336757 403948 519974 351002 351030 351026 403934 336767 336814 336822 336823 336824 336813 336815 336760 336758 351029 336817 230319 262784 ); parentid="403931"; if [[ ! "${array[@]}" =~ "\b${parentid}\b" ]]; then echo "NOT FOUND"; else echo "FOUND"; fi
'''

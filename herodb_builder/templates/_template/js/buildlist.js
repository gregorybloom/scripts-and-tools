var getPath = function(poplvl) {
  var path = window.location.href;
  path = (path.match(/^(.*[\/\\])\s*/mg)).pop();
  path = path.split("/");
  var bit = path.pop();
  console.log(bit,path);
  for(var i=0;i<poplvl;i++)   path.pop();
  console.log(bit,path);

  if( /file\s*[^;]*\bbrowser\s*$/.test(getEngineType(window.location.href)) ) {
      if(bit != "")  path.push(bit);
  }
  else if(engineMode === "node web browser") {
      path.push("static");
  }
  path = path.join("/");
  return path;
}

var filterPostFields = function(fieldname, postfield) {

  var text = postfield.replace(/\\r\\n/gi,'<br>');
  text = text.replace(/\\t/gi,'&nbsp;');
  text = text.replace(/\\n/gi,'<br>');

  text = text.replace(/\[(playergm|talk|thought|action|ooc|radio)\]/, function(a, b){
      return '<span class="postformatting '+b+'"><span class="formattext formatopen">[' + b + ']</span>';
  });
  text = text.replace(/\[\/(playergm|talk|thought|action|ooc|radio)\]/, function(a, b){
      return '<span class="formattext formatclose">[/' + b + ']</span></span>';
  });

  var copen = text.split("<span class=\"formattext formatopen\">[").length-1;
  var cclose = text.split("<span class=\"formattext formatclose\">[").length-1;
  if (copen > cclose) {
    for(var i=cclose; i<copen;c++) {
      text = text + '</span>';
    }
  }

  if(fieldname == "postdate")  text = text.replace(/\-\d+$/,'');
  if(fieldname == "postdate")  text = text.replace(/\.\d+$/,'');
  if(fieldname == "postdate")  text = text.replace(/\s+(?=\d\d\:)/,'&nbsp;&nbsp;&nbsp;');

  return text;
};
var getNameText = function(post,loaditems,type,id) {
  if(type == 'user') {
    if( typeof loaditems["user"][id] === "undefined" )      return "[N/A]";
    return loaditems["user"][id]['displayname'];
  }
  if(type == 'char') {
      if( typeof loaditems["char"][id] === "undefined" )      return "[N/A]";
      return loaditems["char"][id]['charactername'];
  }
};

var sortThreads = function(postlist) {
  function isLater(str1, str2)
  {
//      console.log(str1,' < ',str2,'==',(new Date(str1) < new Date(str2)));
      return new Date(str1) < new Date(str2);
  }

  var sortedlist = [];
  var unsortedlist = Object.keys(postlist);

  var c = 0;
  while(unsortedlist.length > 0) {
    var lowdate = null;
    var lowestkey = null;
    var lowi = null;
    for(var i in unsortedlist) {
      var key = unsortedlist[i];
      var date = postlist[key]['postdate'];
      if(lowdate == null) {
          lowdate = date;
          lowestkey = key;
          lowi = i;
      }
      else {
        var later = isLater(lowdate,date);
        if(!later) {
          lowdate = date;
          lowestkey = key;
          lowi = i;
        }
      }
    }
    if(lowestkey != null) {
      unsortedlist.splice(lowi,1);
      sortedlist.push(lowestkey);
    }
    c=c+1;
    if(c > (Object.keys(postlist).length+5))    {console.log("FSUDCSDF");return;}
  }
  return sortedlist;
};

var loadNext = function(list,items,pos,callback) {
  if(pos >= list.length) {
    if(typeof callback === "function")    callback.call(this);
  }
  else {
    var url = list[pos].url;
    var _items = items;
    asyncBrowserLoad(url,{},function(e) {
      console.log('_items["'+list[pos].type+'"]["'+list[pos].id+'"] = JSONDATA_'+list[pos].type.toUpperCase()+'_'+list[pos].id+';');
      eval('_items["'+list[pos].type+'"]["'+list[pos].id+'"] = JSONDATA_'+list[pos].type.toUpperCase()+'_'+list[pos].id+';');
      loadNext(list,_items,pos+1,callback);
    }.bind(document));
  }
};
var buildPostList = function(postlistdata, mode, type, doc, callback) {
  var poplvl = 0;
//  if(NAME == "INDEX")   poplvl = 1;
  var path = getPath(poplvl);
  console.log(postlistdata);

  console.log(path +"/_data/lists/js/userlist.js");
  asyncBrowserLoad(path +"/_data/lists/js/userlist.js",{},function(e) {
    var loaditems = {};
    loaditems.char = {};
    loaditems.user = {};

    var loadlist = [];
    for(var i in JSONDATA_USERLIST['users']) {
        loadlist.push({url:path +"/_data/users/js/"+i+".js",type:'user',id:i});
    }
    for(var i in JSONDATA_USERLIST['chars']) {
      loadlist.push({url:path +"/_data/characters/js/"+i+".js",type:'char',id:i});
    }
    loadNext(loadlist,loaditems,0,function(e) {




      var ListDiv = $('#postlistdiv');
      var keylist = sortThreads(postlistdata);

      for(var i in keylist) {
          var postdata = postlistdata[keylist[i]];
          console.log(i, type, postdata);

          dLinkDiv = document.createElement('div');
          $(dLinkDiv).addClass("linkdiv");
          ListDiv.append(dLinkDiv);

              dLinkFront = document.createElement('div');
              $(dLinkFront).addClass("linkdivfront");
              dLinkDiv.append(dLinkFront);


                  dLink = document.createElement('a');
                  dLink.href = path + "/posts/dynamic/"+ type +"/"+ postdata['postid'] +".html";
                  dLink.innerHTML = "/posts/dynamic/"+ type +"/"+ postdata['postid'] +".html";
                  dLinkFront.append(dLink);


                  dSpan = document.createElement('span');
                  $(dSpan).addClass("linkdivtitle");
                  dSpan.innerHTML = postdata['posttitle'];
                  dLinkFront.append(dSpan);


              dLinkBack = document.createElement('div');
              $(dLinkBack).addClass("linkdivback");
              dLinkDiv.append(dLinkBack);


                  dChar = document.createElement('span');
                  $(dChar).addClass("linkchar");
                  dChar.innerHTML = filterPostFields('postchar', getNameText(postdata,loaditems,'char',postdata['userid']));
                  dLinkBack.append(dChar);
                  dUser = document.createElement('span');
                  $(dUser).addClass("linkuser");
                  dUser.innerHTML = filterPostFields('postuser', getNameText(postdata,loaditems,'user',postdata['userid']));
                  dLinkBack.append(dUser);
/**/

                  dDate = document.createElement('div');
                  $(dDate).addClass("linkdivdate");
                  dDate.innerHTML = filterPostFields('postdate',postdata['postdate']);
                  dLinkBack.append(dDate);

      }




    }.bind(document));
  }.bind(document));





/*
    loadNext(loadlist,loaditems,0,function(e) {
      buildPostWalk(postdata,loaditems,doc,div,1,callback);
    }     /**/
};

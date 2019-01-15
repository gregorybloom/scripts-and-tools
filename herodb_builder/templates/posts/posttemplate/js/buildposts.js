var POSTPAD = 25;


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

  if(fieldname == "postdate")  text = text.replace(/\.\d+(?:-\d*)?$/,'');
  if(fieldname == "postdate")  text = text.replace(/\s+(?=\d\d\:)/,'&nbsp;&nbsp;&nbsp;');

  return text;
};
var getNameText = function(post,loaditems,type,id) {
  if(type == 'user') {
    if( typeof loaditems["user"][id] === "undefined" )      return "[N/A]";
    return loaditems["user"][id]['displayname'];
  }
  if(type == 'char') {
    console.log(post['_postdata']);
    if( typeof post['_postdata']['charactername'] === "undefined" ) {
        if( typeof loaditems["char"][id] === "undefined" )      return "[N/A]";
        return loaditems["char"][id]['charactername'];
    }
    if( post['_postdata']['charactername'].match(/[\\\/][nN]$/) ) {
      if( typeof loaditems["char"][id] === "undefined" )      return "[N/A]";
      return loaditems["char"][id]['charactername'];
    }
    return post['_postdata']['charactername'];
  }
};
var addPost = function(post, doc, loaditems, parentdiv, depth) {
  d = document.createElement('div');
  $(d).addClass("postframe");

      dContent = document.createElement('div');
      $(dContent).addClass("postcontent");
      d.append(dContent);

          dHead = document.createElement('div');
          $(dHead).addClass("posthead");
          dContent.append(dHead);

              dTitle = document.createElement('div');
              $(dTitle).addClass("posttitle");
              dTitle.innerHTML = filterPostFields('posttitle', post['_postdata']['posttitle']);
              dHead.append(dTitle);
              dChar = document.createElement('div');
              $(dChar).addClass("postchar");
              dChar.innerHTML = filterPostFields('postchar', getNameText(post,loaditems,'char',post['_postdata']['userid']));
              dHead.append(dChar);
              dUser = document.createElement('div');
              $(dUser).addClass("postuser");
              dUser.innerHTML = filterPostFields('postuser', getNameText(post,loaditems,'user',post['_postdata']['userid']));
              dHead.append(dUser);
              dDate = document.createElement('div');
              $(dDate).addClass("postdate");
              dDate.innerHTML = filterPostFields('postdate', post['_postdata']['postdate']);
              dHead.append(dDate);

          dText = document.createElement('div');
          $(dText).addClass("posttext");
          dText.innerHTML = filterPostFields('postcontent', post['_postdata']['postcontent']);
          dContent.append(dText);

      dSubposts = document.createElement('div');
      $(dSubposts).addClass("postsubposts");
      d.append(dSubposts);

  console.log(post['_indexdata']['postid'], post['_postdata']);

  if(depth > 1) {
    $(d).css({ marginLeft : POSTPAD+'px'});
  }
  return d;
};
var sortSubposts = function(postlist,depth) {
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
      var date = postlist[key]['_postdata']['postdate'];
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


var buildPostWalk = function(post, loaditems, doc, parentdiv, depth, call) {
    var newdiv = addPost(post,doc,loaditems,parentdiv,depth);
    parentdiv.append(newdiv);

    if(typeof post['_subposts'] !== "undefined") {
      var keylist = sortSubposts(post['_subposts'],depth);

      for(var i in keylist) {
        var subpost = post['_subposts'][keylist[i]];
        buildPostWalk(subpost, loaditems, doc, $(newdiv).find('> .postsubposts'), depth+1, call);
      }
    }
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
var buildPostList = function(postdata, mode, doc, callback) {
  var poplvl = 3;
  if(NAME == "INDEX")   poplvl = 1;

  var path = getPath(poplvl);


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
      var div = $('#postdiv');
      buildPostWalk(postdata,loaditems,doc,div,1,callback);
    }.bind(document));
  }.bind(document));
};

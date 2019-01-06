var getEngineType = function(webpath) {
  if( typeof process !== "undefined" && process.versions['electron'] && typeof require === "function" ) {
    return 'electron';
  }
  else if( typeof process !== "undefined" && process.versions['node'] && typeof require === "function" ) {
    return 'node';
  }
  else {
    if( /^file\:\/\/\//.test(webpath) )                         return 'file web browser';
    else if( /^https?\:\/\/[^\/<>]+\:\d+\//.test(webpath) )     return 'node web browser';
    else                                                        return 'web browser';
  }
};
var asyncBrowserLoad = function(url, opts, call) {
    if(typeof opts === "undefined" || opts == null)		opts = {};
//			  based on:				https://stackoverflow.com/questions/12820953/asynchronous-script-loading-callback
    var t = 'script';

    var d = document,
        o = d.createElement(t);
    var ar = d.getElementsByTagName(t);
    var s = ar[ar.length-1];

    if( url.match("^file\:\/\/") )		      o.src = url;
    else if( url.match("^https?\:\/\/") )		o.src = url;
    else  	o.src = '//' + url;

    if(opts['defer'])			o.defer = true;

    var newopts = JSON.parse( JSON.stringify( opts ));
    if (call) { o.addEventListener('load', function (e) { call(newopts, e); }, false); }
    s.parentNode.insertBefore(o, s);
};

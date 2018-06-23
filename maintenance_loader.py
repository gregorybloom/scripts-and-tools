import imp, os, sys

SCRIPTPATH = os.path.dirname(os.path.realpath(sys.argv[0]))


driveutils = imp.load_source('driveutils', SCRIPTPATH+'/python_libs/utils/log_utils.py')
joinlogs = imp.load_source('joinlogs', SCRIPTPATH+'/python_libs/utils/joinlogs.py')
tmplogs = imp.load_source('tmplogs', SCRIPTPATH+'/python_libs/tmplogs/tmplogs.py')

filelist = imp.load_source('filelist', SCRIPTPATH+'/python_libs/list/filelist.py')
folderlist = imp.load_source('folderlist', SCRIPTPATH+'/python_libs/list/folderlist.py')

copydrive = imp.load_source('copydrive', SCRIPTPATH+'/python_libs/mounts/copydrive.py')
findmounts = imp.load_source('findmounts', SCRIPTPATH+'/python_libs/mounts/find_mounts.py')
backupmounts = imp.load_source('backupmounts', SCRIPTPATH+'/python_libs/mounts/backup_mounts.py')

#finddupes = imp.load_source('finddupes', SCRIPTPATH+'/python_libs/find/finddupes.py')
findempties = imp.load_source('folderlist', SCRIPTPATH+'/python_libs/find/findempties.py')
#findowndupes = imp.load_source('findowndupes', SCRIPTPATH+'/python_libs/find/findowndupes.py')
comparedirs = imp.load_source('comparedirs', SCRIPTPATH+'/python_libs/find/comparedirs.py')

killfromlist = imp.load_source('killfromlist', SCRIPTPATH+'/python_libs/kill/killfromlist.py')
killjunkfiles = imp.load_source('killjunkfiles', SCRIPTPATH+'/python_libs/kill/killjunkfiles.py')
killfolders = imp.load_source('killfolders', SCRIPTPATH+'/python_libs/kill/killfolders.py')

splitlogs = imp.load_source('splitlogs', SCRIPTPATH+'/python_libs/logsplit/splitlogs.py')
comparesplit = imp.load_source('comparesplit', SCRIPTPATH+'/python_libs/logsplit/comparesplit.py')
finddupesplit = imp.load_source('finddupesplit', SCRIPTPATH+'/python_libs/logsplit/finddupesplit.py')

dropmissed = imp.load_source('dropmissed', SCRIPTPATH+'/python_libs/validate/drop_missed.py')
comparefns = imp.load_source('comparefns', SCRIPTPATH+'/python_libs/validate/compare_fns.py')
comparesearch = imp.load_source('comparesearch', SCRIPTPATH+'/python_libs/validate/compare_search.py')
comparedata = imp.load_source('comparedata', SCRIPTPATH+'/python_libs/validate/compare_data.py')
checkmd5s = imp.load_source('checkmd5s', SCRIPTPATH+'/python_libs/validate/check_md5logs.py')
finddupes = imp.load_source('finddupes', SCRIPTPATH+'/python_libs/validate/find_md5_dupes.py')

#comparedupes = imp.load_source('comparedupes', SCRIPTPATH+'/python_libs/duplicates/compare_dupes.py')
#checkdupes = imp.load_source('checkdupes', SCRIPTPATH+'/python_libs/duplicates/check_dupes.py')

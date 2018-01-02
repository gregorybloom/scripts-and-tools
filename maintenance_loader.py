import imp

driveutils = imp.load_source('driveutils', 'python_libs/utils/log_utils.py')
joinlogs = imp.load_source('joinlogs', 'python_libs/utils/joinlogs.py')
tmplogs = imp.load_source('tmplogs', 'python_libs/tmplogs/tmplogs.py')

filelist = imp.load_source('filelist', 'python_libs/list/filelist.py')
folderlist = imp.load_source('folderlist', 'python_libs/list/folderlist.py')

copydrive = imp.load_source('copydrive', 'python_libs/mounts/copydrive.py')
findmounts = imp.load_source('findmounts', 'python_libs/mounts/find_mounts.py')
backupmounts = imp.load_source('backupmounts', 'python_libs/mounts/backup_mounts.py')

finddupes = imp.load_source('finddupes', 'python_libs/find/finddupes.py')
findempties = imp.load_source('folderlist', 'python_libs/find/findempties.py')
findowndupes = imp.load_source('findowndupes', 'python_libs/find/findowndupes.py')
comparedirs = imp.load_source('comparedirs', 'python_libs/find/comparedirs.py')

killfromlist = imp.load_source('killfromlist', 'python_libs/kill/killfromlist.py')
killjunkfiles = imp.load_source('killjunkfiles', 'python_libs/kill/killjunkfiles.py')
killfolders = imp.load_source('killfolders', 'python_libs/kill/killfolders.py')

splitlogs = imp.load_source('splitlogs', 'python_libs/logsplit/splitlogs.py')
comparesplit = imp.load_source('comparesplit', 'python_libs/logsplit/comparesplit.py')
finddupesplit = imp.load_source('finddupesplit', 'python_libs/logsplit/finddupesplit.py')

comparedata = imp.load_source('comparedata', 'python_libs/validate/compare_data.py')
checkmd5s = imp.load_source('checkmd5s', 'python_libs/validate/check_md5logs.py')

comparedupes = imp.load_source('comparedupes', 'python_libs/duplicates/compare_dupes.py')
checkdupes = imp.load_source('checkdupes', 'python_libs/duplicates/check_dupes.py')

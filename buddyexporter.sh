#!/bin/bash

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`

source "$SCRIPTDIR/bash_libs/handle_mounts.sh"
source "$SCRIPTDIR/bash_libs/handle_logs.sh"

IFS=$'\n'

echo "Running: $SCRIPTPATH"

OPTS=`getopt -o vh: --long verbose,help,filepath: -n 'parse-options' -- "$@"`
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi


#####################################
# Help function
help() {
  cat <<EndHelp
  buddyexporter.sh - Detect flagged drives and auto-backup
  Usage: buddyexporter.sh --filepath TYPE
  --runtype
  Type of backup run
EndHelp
  exit 0
}
####################################
loadopts() {
  echo "$OPTS"
  eval set -- "$OPTS"

  VERBOSE=false
  HELP=false
  FILEPATH=false

  while true; do
   case "$1" in
    -v | --verbose ) VERBOSE=true; shift ;;
    -h | --help )    HELP=true; shift ;;
    --filepath )   FILEPATH="$2"; shift 2 ;;
    -- ) shift; break ;;
    * ) break ;;
   esac
  done

  echo VERBOSE=$VERBOSE
  echo HELP=$HELP
  echo FILEPATH=$FILEPATH
}

exportbuddysession() {
  path="$1"
  tfile="$2"
  tmppath="$3"
  resultfile="$4"

  touch "$resultfile"

  fullpath="$path/$tfile"
  tmpfilepath="$tmppath/ex_$tfile.txt"

  rm -Rvf "$tmppath"
  mkdir -p "$tmppath"
  cp "$fullpath" "$tmpfilepath"
  strings "$tmpfilepath" > "$tmppath/ex_$tfile.tmp.txt"

  startnum=$(grep -m 1 -niP "^20\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d{3}Z" "$tmppath/ex_$tfile.tmp.txt" | grep -oP "^\d+(?=\:)")
  endnum=$(wc -l "$tmppath/ex_$tfile.tmp.txt")
  echo "$startnum,$endnum"

  c=0
  tail -n+"$startnum" "$tmppath/ex_$tfile.tmp.txt" > "$tmppath/ex_$tfile.tmpclip.$c.txt"

  wc -l "$tmppath/ex_$tfile.tmpclip.$c.txt"
  until [ $(wc -l "$tmppath/ex_$tfile.tmpclip.$c.txt" | grep -oP "^\d+") -eq 0 ]; do
    snum=$(grep -m 1 -niP "^20\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d{3}Z" "$tmppath/ex_$tfile.tmpclip.$c.txt" | grep -oP "^\d+(?=\:)")
    snum=1
    enum=$(grep -m 1 -nP ",\"top\"\:\d+,\"type\"\:\"normal\",\"width\"\:\d+\}\]\s*$" "$tmppath/ex_$tfile.tmpclip.$c.txt" | grep -oP "^\d+(?=\:)")
    echo "$snum,$enum"

    tail -n+"$snum" "$tmppath/ex_$tfile.tmpclip.$c.txt" | head -n "$enum" > "$tmppath/ex_$tfile.misc.txt"
    tr -d '\012' < "$tmppath/ex_$tfile.misc.txt" > "$tmppath/ex_$tfile.miscclip.$c.txt"
    cat "$tmppath/ex_$tfile.miscclip.$c.txt" >> "$resultfile"

    enum=$((enum+1))
    tail -n+"$enum" "$tmppath/ex_$tfile.tmpclip.$c.txt" > "$tmppath/ex_$tfile.tmpclip.tmp.txt"

#    c=$((c+1))
    rm -f "$tmppath/ex_$tfile.tmpclip.$c.txt"
    mv "$tmppath/ex_$tfile.tmpclip.tmp.txt" "$tmppath/ex_$tfile.tmpclip.$c.txt"

    wc -l "$tmppath/ex_$tfile.tmpclip.$c.txt"
    if grep -m 1 -qP "^20\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d{3}Z" "$tmppath/ex_$tfile.tmpclip.$c.txt"; then
      continue
    fi
    exit 0
  done
}




loadopts



#DRIVEFILE="_DRIVEFLAG_PROJECT_NETDRIVE_"
RUNNAME="exporter"

RUNTMPPATH="/tmp/autobackup/bextmp/$RUNNAME"
mkdir -p "$RUNTMPPATH"

rm -f "$RUNTMPPATH/mounted.txt"
loadmounts "$RUNTMPPATH" "mounted.txt"
verifydriveflags "$RUNTMPPATH"


if grep -iqP "\/drives\/c\b" "$RUNTMPPATH/mounted.txt"; then
  flagfile=$(grep -inrP "\/drives\/c\b" "$RUNTMPPATH/mounted.txt" | grep -oP "(?<=,)_DRIVEFLAG_\w+")
else
  echo "No home drive found. Exiting..."
  exit 0
fi


driveflagname=$(echo "$flagfile" | grep -oP "(?<=_DRIVEFLAG_)\w+(?=_\s*)" | tr '[:upper:]' '[:lower:]')


thedate="$(date +'%Y%m%d_T%H%M%S')"
tuser=$(whoami)
sourcepath="/drives/c/Users/$tuser"

############ USE MOUNT TO FIND DRIVEFLAG NAME
backuppath="$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/logs/$thedate/sessionbuddy_$thedate.txt"
if [ ! -d "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/" ]; then
  mkdir "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/"
fi
#if [ ! -d "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/logs/" ]; then
#  mkdir "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/logs/"
#  mkdir "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/logs/$thedate/"
#elif [ ! -d "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/logs/$thedate/" ]; then
#  mkdir "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/logs/$thedate/"
#fi
if [ ! -d "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/core/" ]; then
  mkdir "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/core/"
fi
if [ ! -d "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/core/$thedate/" ]; then
  mkdir "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/core/$thedate/"
else
  echo "Already has the date.  Wait a minute and try again."
  exit 0
fi

extensionstartname="chrome-extension_"
extensionhash="edacconmaakjimmfgnblocblbcdcpbko"
extensionstartpath="/AppData/Local/Google/Chrome/User Data/Default/databases/"
for filepath in $(ls -l "$sourcepath$extensionstartpath" | grep -oP "$extensionstartname$extensionhash\w+(?=\s*$)"); do
  opath="$sourcepath$extensionstartpath$filepath"
  for last in $(ls -l "$opath" | grep -oP "(?<=\s)\w+$"); do
    if [ -f "$opath/$last" ]; then
      cp "$opath/$last" "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/core/$thedate/sessioncore_$last__$thedate"
#      exportbuddysession "$opath" "$last" "$RUNTMPPATH" "$backuppath"
    fi
  done
done

removeoldlogs "$sourcepath/BackupSelf/SessionBuddy_Backups/$driveflagname/core/" "^(\d{8}_T\d+)\s*$" "$RUNTMPPATH" 10

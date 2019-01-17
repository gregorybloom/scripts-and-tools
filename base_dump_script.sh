#!/bin/bash
SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`

IFS=$'\n'

OPTS=`getopt -o vh: --long help,verbose,pullserver,discordall,discorddl,discordcomp,discordpack,cloud,cloudonly,tryalso:,tryinstead:,cloudtryalso:,cloudtryinstead:,nodump,runcomp: -n 'parse-options' -- "$@"`
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi
loadopts() {
  echo "$OPTS"
  eval set -- "$OPTS"

  VERBOSE=false
  HELP=false

  PULLSERVER=false
  DISCORDRUN=false
  DISCORDTYPE=0

  CLOUDRUN=false
  CLOUDBASIC=false

  DUMPBACKUP=true
  DUMPBASICS=true

  BACKUPRUNSET=false
  CLOUDRUNSET=false
  while true; do
   case "$1" in
    -v | --verbose ) VERBOSE=true; shift ;;
    -h | --help )    HELP=true; shift ;;

    --runcomp )   RUN_COMP="$2"; shift 2 ;;
    --nodump )    DUMPBACKUP=false; DUMPBASICS=false; shift ;;
    --tryalso )   BACKUPRUNSET="$2"; shift 2 ;;
    --tryinstead )   DUMPBASICS=false; BACKUPRUNSET="$2"; shift 2 ;;

    --pullserver )  PULLSERVER=true; shift ;;
    --discordall )   DISCORDRUN=true; DISCORDTYPE=3; shift ;;
    --discordpack )   DISCORDRUN=true; DISCORDTYPE=2; shift ;;
    --discordcomp )   DISCORDRUN=true; DISCORDTYPE=2; shift ;;
    --discorddl )   DISCORDRUN=true; DISCORDTYPE=1; shift ;;

    --cloud )     CLOUDRUN=true; CLOUDBASIC=true; shift ;;
    --cloudonly )   CLOUDRUN=true; CLOUDBASIC=true; DUMPBACKUP=false; DUMPBASICS=false; shift ;;

    --cloudtryalso )   CLOUDRUNSET="$2"; shift 2 ;;
    --cloudtryinstead )   CLOUDBASIC=false; CLOUDRUNSET="$2"; shift 2 ;;
    -- ) shift; break ;;
    * ) break ;;
    esac
  done
}
loadopts

source "$SCRIPTDIR/bash_libs/handle_mounts.sh"

if [ "$RUN_COMP" == "alita" ]; then
    source "$SCRIPTDIR/config/launcherinfo/alitadump_info.sh"
elif [ "$RUN_COMP" == "asirpa" ]; then
    source "$SCRIPTDIR/config/launcherinfo/asirpadump_info.sh"
elif [ "$RUN_COMP" == "lenovo" ]; then
    source "$SCRIPTDIR/config/launcherinfo/lenovodump_info.sh"
  elif [ "$RUN_COMP" == "desktop" ]; then
      source "$SCRIPTDIR/config/launcherinfo/desktopdump_info.sh"
else
    echo "No computer declared."
    exit 0
fi


backuprunlist=false
if [ "$DUMPBACKUP" == true ] ; then
  if [ "$DUMPBASICS" == true ] ; then
    backuprunlist=($RUNNAME)
  fi
  if echo "$BACKUPRUNSET" | grep -qP "^\w+\s*(?:,\s*\w+)*$"; then
      backuprunlist=(${BACKUPRUNSET//,/
})
  fi
fi

cloudrunlist=false
if [ "$CLOUDRUN" == true ]; then
  if [ "$CLOUDBASIC" == true ]; then
    cloudrunlist=($CLOUDRUNNAME)
  fi
  if echo "$CLOUDRUNSET" | grep -qP "^\w+\s*(?:,\s*\w+)*$"; then
      cloudrunlist=(${CLOUDRUNSET//,/
})
  fi
fi


mkdir -p "$RUNTMPPATH"
rm -f "$RUNTMPPATH/mounted.txt"

echo "loading mounts"
loadmounts "$RUNTMPPATH" "mounted.txt"

echo "verifying drive flags"
builddrivepaths "$RUNTMPPATH" "$RUNTMPPATH/drives.txt"
#verifydriveflags "$RUNTMPPATH"

if grep -qP "$DRIVEFILE" "$RUNTMPPATH/drives.txt"; then
  value=$(grep -P "\b$DRIVEFILE\b" "$RUNTMPPATH/drives.txt")
  basedrive=$(echo "$value" | grep -oP "(?<=,)\/[^,]+(?=,\w+,\w+)")
else
  echo "NO $DRIVEFILE FOUND"
  exit 0
fi
echo "done locating targets"

sourcepath="$basedrive/"

tuser=$(whoami)
if [ ! -z ${SCRIPTFOLDERPATH+x} ]; then
  lastdir="$basedrive/$SCRIPTFOLDERPATH"
else
  lastdir=$(echo "$SCRIPTDIR" | grep -oP "^.*(?=\/)")
fi

if [ "$PULLSERVER" == true ]; then
  (cd ..;/bin/bash "$lastdir"/backup_102.sh)
  (cd ..;/bin/bash "$lastdir"/backup_111.sh)
fi
if [ "$DISCORDRUN" == true ]; then
  case "$DISCORDTYPE" in
    1) python "$lastdir"/discord_exporter.py; shift ;;
    2) python "$lastdir"/discord_exporter.py compileonly; shift ;;
    3) python "$lastdir"/discord_exporter.py scanall; shift ;;
    0) break ;;
    *) break ;;
  esac
fi

if [ "$DUMPBACKUP" == true ] ; then
  if [ ! "$backuprunlist" == false ] ; then
    for back in ${backuprunlist[@]}; do
        runtext="$back"
        /bin/bash "$lastdir"/autobackup.sh --runtype="$runtext" --force --sourcescript="$sourcepath"
      done
  fi
fi
if [ "$CLOUDRUN" == true ]; then
  if [ ! "$cloudrunlist" == false ] ; then
    for back in ${cloudrunlist[@]}; do
        runtext="$back"
        value=$(grep -P "$CLOUDDRIVEFILE" "$RUNTMPPATH/drives.txt")
        clouddrive=$(echo "$value" | grep -oP "(?<=,)\/[^,]+(?=,\w+,\w+)")
        /bin/bash "$lastdir"/autobackup.sh --runtype="$runtext" --force --sourcescript="$clouddrive/"
      done
  fi
fi

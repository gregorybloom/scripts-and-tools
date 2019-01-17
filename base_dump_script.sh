#!/bin/bash
SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`

IFS=$'\n'

OPTS=`getopt -o vh: --long help,verbose,pullserver,discordall,discorddl,discordcomp,discordpack,cloud,cloudonly,filedump,nodump,runcomp: -n 'parse-options' -- "$@"`
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
  CLOUDTYPE=0
  DUMPBACKUP=true
  DUMPFILES=false

  while true; do
   case "$1" in
    -v | --verbose ) VERBOSE=true; shift ;;
    -h | --help )    HELP=true; shift ;;
    --runcomp )   RUN_COMP="$2"; shift 2 ;;
    --pullserver )  PULLSERVER=true; shift ;;
    --discordall )   DISCORDRUN=true; DISCORDTYPE=3; shift ;;
    --discordpack )   DISCORDRUN=true; DISCORDTYPE=2; shift ;;
    --discordcomp )   DISCORDRUN=true; DISCORDTYPE=2; shift ;;
    --discorddl )   DISCORDRUN=true; DISCORDTYPE=1; shift ;;

    --cloud )     CLOUDRUN=true; CLOUDTYPE=1; shift ;;
    --cloudonly )   CLOUDRUN=true; CLOUDTYPE=2; DUMPBACKUP=false; shift ;;
    --filedump )    DUMPFILES=true; shift ;;
    --nodump )    DUMPBACKUP=false; shift ;;

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


mkdir -p "$RUNTMPPATH"
rm -f "$RUNTMPPATH/mounted.txt"

echo "loading mounts"
loadmounts "$RUNTMPPATH" "mounted.txt"

echo "verifying drive flags"
builddrivepaths "$RUNTMPPATH" "$RUNTMPPATH/drives.txt"
#verifydriveflags "$RUNTMPPATH"

if grep -qP "$DRIVEFILE" "$RUNTMPPATH/drives.txt"; then
  value=$(grep -P "$DRIVEFILE" "$RUNTMPPATH/drives.txt")
  basedrive=$(echo "$value" | grep -oP "(?<=,)\/[^,]+(?=,\w+,\w+)")
else
  echo "NO $DRIVEFILE FOUND"
  exit 0
fi
echo "done locating targets"

DOSOURCE=true
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
  if [ "$DOSOURCE" == false ]; then
    /bin/bash "$lastdir"/autobackup.sh --runtype="$RUNNAME" --force
  else
    /bin/bash "$lastdir"/autobackup.sh --runtype="$RUNNAME" --force --sourcescript="$sourcepath"
  fi
  if [ "$DUMPFILES" == true ] ; then
    if [ "$DOSOURCE" == false ]; then
      /bin/bash "$lastdir"/autobackup.sh --runtype="$RUNNAMEEXTRA" --force
    else
      /bin/bash "$lastdir"/autobackup.sh --runtype="$RUNNAMEEXTRA" --force --sourcescript="$sourcepath"
    fi
  fi
fi
if [ "$CLOUDRUN" == true ]; then
  if grep -qP "$CLOUDDRIVEFILE" "$RUNTMPPATH/drives.txt"; then
    value=$(grep -P "$CLOUDDRIVEFILE" "$RUNTMPPATH/drives.txt")
    clouddrive=$(echo "$value" | grep -oP "(?<=,)\/[^,]+(?=,\w+,\w+)")
    /bin/bash "$lastdir"/autobackup.sh --runtype="$CLOUDRUNNAME" --force --sourcescript="$clouddrive/"
  fi
fi

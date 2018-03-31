#!/bin/bash
IFS=$'\n'

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`

OPTS=`getopt -o vh: --long verbose,force,help,email,precheck,vcheck,preponly,verbose,sourcescript:,runtype: -n 'parse-options' -- "$@"`
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi

source "$SCRIPTDIR/config/autobackup_config.sh"
source "$SCRIPTDIR/bash_libs/scrape_swaks.sh"
source "$SCRIPTDIR/bash_libs/lock_and_tmp_files.sh"
source "$SCRIPTDIR/bash_libs/handle_mounts.sh"
source "$SCRIPTDIR/bash_libs/parse_output.sh"

#####################################
# Help function
help() {
  cat <<EndHelp
  autobackup.sh - Detect flagged drives and auto-backup
  Usage: autobackup.sh --runtype TYPE
  --runtype
  Type of backup run
EndHelp
  exit 0
}
####################################

hasfunct() {
  testfn="$1"
  if [ "$testfn" == "blockid" ]; then
    $(blkid > /dev/null 2>&1)
    if [ "$?" -eq 127 ]; then
      false
    else
      true
    fi
  elif [ "$testfn" == "mail" ]; then
   $(mail > /dev/null 2>&1)
   if [ "$?" -eq 127 ]; then
    false
  else
    true
  fi
elif [ "$testfn" == "swaks" ]; then
 $(swaks --version > /dev/null 2>&1)
 if [ "$?" -eq 127 ]; then
  false
else
  true
fi
fi
}
loadopts() {
  echo "$OPTS"
  eval set -- "$OPTS"

  VERBOSE=false
  HELP=false
  VALID_CHECK=false
  PREP_ONLY=false
  IGNORE_LOCKS=false
  BACKUP_VERBOSE=false

  while true; do
   case "$1" in
-v | --verbose ) VERBOSE=true; shift ;;
-h | --help )    HELP=true; shift ;;
--runtype )   RUN_TYPE="$2"; shift 2 ;;
--sourcescript )  SOURCE_SCRIPT="$2"; shift 2 ;;
--force )   IGNORE_LOCKS=true; shift ;;
--precheck ) PRE_CHECK=true; shift ;;
--email )   USE_EMAIL=true; shift ;;
--vcheck )  VALID_CHECK=true; shift ;;
--preponly )  PREP_ONLY=true; shift ;;
--verbose )  BACKUP_VERBOSE=true; shift ;;
-- ) shift; break ;;
* ) break ;;
esac
done

echo PREP_ONLY=$PREP_ONLY
echo VALID_CHECK=$VALID_CHECK
echo RUN_TYPE=$RUN_TYPE
}
loadrundata() {
  if [ "$RUN_TYPE" == false ]; then
    exit 1
  fi
  if [ "$RUN_TYPE" ]; then
    if echo "$RUN_TYPE" | grep -qP "^\s*[\w\-]+\s*$"; then
      return 0
    else
      echo "BAD INPUT"
      exit 1
    fi
  fi
}
sourcematch() {
  sourcescriptpath="$1"
  if [[ $SCRIPTPATH == $sourcescriptpath* ]]; then
    true
  elif [ ! "$SOURCE_SCRIPT" == false ]; then
    if [[ $SOURCE_SCRIPT == $sourcescriptpath* ]]; then
      true
    else
      false
    fi
  else
    false
  fi
}
#####################################
findcopypaths() {
  touch "$RUNTMPPATH/copypaths.txt"
  for j in $(cat "$RUNTMPPATH/mounted.txt"); do
    IFS=',' read -ra vals5 <<< "$j"    #Convert string to array

    opath=${vals5[0]}
    path=${vals5[1]}
    type=${vals5[2]}
    driveflag=${vals5[3]}
    backupflags=()

    if sourcematch "$path"; then
      for k in $(ls -l "$path"); do
        if echo "$k" | grep -qP "^\-[\w\-\.\+]+\s*\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\d+\s+(?:\d+\:)?\d+\s+_BACKUPFLAG_\w+_\.txt\s*$"; then

          # ADD BACKUP FLAGS ONLY IF THEY COME FROM SAME DRIVE AS SCRIPT
          bkupflag=$(echo "$k" | grep -oP "(?<=\s)_BACKUPFLAG_\w+_(?=\.txt\s*$)")
          if [ -f "$path/$bkupflag.txt" ]; then
            backupflags+=($bkupflag)
          fi
        fi
      done
    else
      echo "$path skipped - is not source from script path: $SCRIPTPATH"
    fi

    for back in ${backupflags[@]}; do
#      backfile="${backupflags["$back"]}"
      backfile="$back"

      if [ -f "$path/$backfile.txt" ]; then
        for m in $(cat "$path/$backfile.txt"); do

          if echo "$m" | grep -qP "^\s*\w+,\d+,_\w+_,"; then

            #      $runname,$copystep,$sourceflag,$sourcepath,$targetflag,$targetpath
            IFS=',' read -ra vals6 <<< "$m"    #Convert string to array
            runname=${vals6[0]}
            copystep=${vals6[1]}
            sourceflag=${vals6[2]}
            sourcepath=${vals6[3]}
            targetflag=${vals6[4]}
            targetpathM=${vals6[5]}
#	    targetpath=$(echo "$targetpathM")
            targetpath=$(echo "$targetpathM" | sed -e "s/[]//g")


            DEST_FOUND=false
            SOURCE_FOUND=false
            SOURCE_MATCHES_SELF=false

            if [ "$RUN_TYPE" == "$runname" ]; then
              if [ "$driveflag" == "$sourceflag" ]; then
                SOURCE_FOUND=true
                if sourcematch "$path"; then
                  SOURCE_MATCHES_SELF=true

                  for n in $(cat "$RUNTMPPATH/mounted.txt"); do
                    IFS=',' read -ra vals7 <<< "$n"    #Convert string to array
                    targetflag2=${vals7[3]}
                    if [[ "$targetflag" == "$targetflag2" ]]; then
                      targetdrivepath=${vals7[1]}
                      DEST_FOUND=true
                      break
                    fi
                  done
                fi
              fi
              if [ "$DEST_FOUND" == true ]; then
                drivepath=$(echo "$path")
                echo "$runname,$copystep,$drivepath,$sourceflag,$sourcepath,$targetdrivepath,$targetflag,$targetpath" >> "$RUNTMPPATH/copypaths.txt"
                echo "$runname,$copystep,$drivepath,$sourceflag,$sourcepath,$targetdrivepath,$targetflag,$targetpath"

                if [ "$SOURCE_FOLDERPATH" == false ]; then
		                SOURCE_FOLDERPATH="$drivepath"
                fi

              elif [ "$SOURCE_MATCHES_SELF" == true ]; then
                echo "destination drive '$targetflag' not found"
                ERROR_FAIL=true
                touch "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                echo -e "ERROR: DESTINATION DRIVE '$targetflag' NOT FOUND\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                cat "$RUNTMPPATH/mounted.txt" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                echo -e "--------------------------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
              elif [ "$SOURCE_FOUND" == true ]; then
                echo "sourceflag '$sourceflag' doesn't match script's source"
                ERROR_FAIL=true
                touch "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                echo -e "ERROR: SOURCE DRIVE '$sourceflag' MISMATCH WITH SCRIPT SOURCE\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                cat "$RUNTMPPATH/mounted.txt" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                echo -e "--------------------------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
              else
                echo "source drive '$sourceflag' not found"
                ERROR_FAIL=true
                touch "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                echo -e "ERROR: SOURCE DRIVE '$sourceflag' NOT FOUND\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                cat "$RUNTMPPATH/mounted.txt" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                echo -e "--------------------------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
              fi
            fi
          fi
        done
      fi
    done
    #
  done
}
scanrsync() {
  testrun=$1
  pathsfile="$2"                  # $RUNTMPPATH/copypaths.txt
  tmperrfile="$3"                 # $RUNLOGPATH/prelog_errs-$LOGSUFFIX
  tmplog="$4"                     # $RUNTMPPATH/rsynclog.txt
  errdump="$ERRDUMP_FILEPATH"        # $ERRDUMP_FILEPATH
  for j in $(cat "$pathsfile"); do
    IFS=',' read -ra vals8 <<< "$j"    #Convert string to array

    runname=${vals8[0]}
    copystep=${vals8[1]}
    drivepath=${vals8[2]}
    sourceflag=${vals8[3]}
    sourcepath=${vals8[4]}
    targetdrivepath=${vals8[5]}
    targetflag=${vals8[6]}
    targetpath=${vals8[7]}

    mkdir -p "$targetdrivepath/$targetpath"
    LOOP_ERROR_FAIL=false

    if [ "$testrun" == true ]; then
      errdumpltr="c"
    else
      errdumpltr="e"
    fi

    echo -e "\n--------- $sourcepath ----------\n" >> "$tmperrfile.tmp"
    rm -f "$tmplog"
    if [ -e "$drivepath/$sourcepath" ] && [ -e "$targetdrivepath/$targetpath" ]; then
      touch "$tmplog"
      echo -e "\n--------- $sourcepath ----------\n"
      basev="-hrltzWPSD"
      extend="--no-links --stats --no-compress "
      if [ -d "$drivepath/$sourcepath" ]; then
        extend+="--delete --delete-after "
      fi
      if [ "$testrun" == true ]; then
        extend+="--dry-run "
      fi
      if [ "$BACKUP_VERBOSE" == true ]; then
        basev+="vv"
      fi
      echo "rsync $drivepath/$sourcepath $targetdrivepath/$targetpath"
      eval "rsync $basev $extend --log-file='$tmplog' '$drivepath/$sourcepath' '$targetdrivepath/$targetpath'"

    elif [ ! -e "$drivepath/$sourcepath" ]; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo -e "ERROR: PATH '$drivepath/$sourcepath' NOT FOUND for source drive '$sourceflag'\n" >> "$tmperrfile.tmp"
      echo -e "--------------------------\n" >> "$tmperrfile.tmp"

      echo "--$errdumpltr/1-- $sourcepath : $j" >> "$errdump"
      echo "-- -- -- $drivepath/$sourcepath" >> "$errdump"
    elif [ ! -e "$targetdrivepath/$targetpath" ]; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo -e "ERROR: PATH '$targetdrivepath/$targetpath' NOT FOUND for target drive '$targetflag'\n" >> "$tmperrfile.tmp"
      echo -e "--------------------------\n" >> "$tmperrfile.tmp"

      echo "--$errdumpltr/2-- $sourcepath : $j" >> "$errdump"
      echo "-- -- -- $targetdrivepath/$targetpath" >> "$errdump"
    fi

    if [ "$testrun" == true ]; then
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/pre_rsync-$LOGSUFFIX"
      cat "$tmplog" >> "$RUNLOGPATH/pre_rsync-$LOGSUFFIX"
    else
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/rsync-$LOGSUFFIX"
      cat "$tmplog" >> "$RUNLOGPATH/rsync-$LOGSUFFIX"
    fi

    if [ "$?" == "0" ]; then
      echo "Successful rsync."
    else
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      errlabel=$(getrsyncerrcode "$?")
      echo -e "------ $? : $errlabel : $sourcepath ------\n" >> "$tmperrfile.tmp"
      ################################################ ERRORED HERE, e/3
      echo "--$errdumpltr/3-- $j" >> "$errdump"
      echo "-- -- -- $? : $errlabel : $sourcepath" >> "$errdump"
    fi

    parseresult=$(grepRSyncFailure "$prefregstr" "$tmplog" "$tmperrfile.tmp")
    if echo "$parseresult" | grep -qP "fail_\d+"; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true

      echo "--$errdumpltr/4-- $sourcepath : $j" >> "$errdump"
      grepRSyncFailure "$prefregstr" "$tmplog" "$errdump"
    fi
    ############### DIFFERS AT THIS POINT

    if [ "$testrun" == false ]; then
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_deletes-$LOGSUFFIX"
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_copies-$LOGSUFFIX"
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_folders-$LOGSUFFIX"
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_matches-$LOGSUFFIX"
      grep -P "^$prefregstr\s*deleting\s+.*" "$tmplog" >> "$RUNLOGPATH/log_deletes-$LOGSUFFIX"
      grep -P "^$prefregstr\s*>f\+{9,10}\s+\S.*[^\s\/]\s*$" "$tmplog" >> "$RUNLOGPATH/log_copies-$LOGSUFFIX"
      grep -P "^$prefregstr\s*cd\+{9,10}\s+\S.*\/\s*$" "$tmplog" >> "$RUNLOGPATH/log_folders-$LOGSUFFIX"
      grep -P "^$prefregstr\s*\S.*\s+is uptodate\s*$" "$tmplog" >> "$RUNLOGPATH/log_matches-$LOGSUFFIX"

      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
      parsersync "$tmplog" "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    fi
    ###############

    if [ "$LOOP_ERROR_FAIL" == true ]; then
      cat "$tmperrfile.tmp" >> "$tmperrfile"
    fi
    rm -f "$tmperrfile.tmp"
  done
}
mailout() {
  type="$1"
  outfile="$RUNLOGPATH/log_tmp-$LOGSUFFIX"
  rm -f "$outfile"
  SUBJECT=""
  if [ "$type" == "locked" ]; then
    SUBJECT="autobkup-LOCKED: $thedate1 $RUN_TYPE"
    echo "LOCKED AT $locktime by $BASELOCKPATH/$RUN_TYPE.lock.txt" > "$outfile"
    echo "$thedate1  =  -" >> "$outfile"
  elif [ "$type" == "pre_error" ]; then
    SUBJECT="autobkup-PRE_ERROR: $thedate1 $RUN_TYPE"
    fileone="$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
    echo -e "$SUBJECT\n" > "$outfile"
    echo -e "$thedate1  =  $thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
    if [ "$ERROR_FAIL" == true ]; then
      fileone2="$RUNLOGPATH/log_errs-$LOGSUFFIX"
      echo "\n==========\n\n" >> "$outfile"
      cat "$fileone2" >> "$outfile"
    fi
  elif [ "$type" == "error" ]; then
    SUBJECT="autobkup-ERROR: $thedate1 $RUN_TYPE"
    fileone="$RUNLOGPATH/log_errs-$LOGSUFFIX"
    fileone2="$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    echo -e "$SUBJECT\n" > "$outfile"
    echo -e "$thedate1  =  $thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
    cat "$fileone2" >> "$outfile"
  elif [ "$type" == "prep_only" ]; then
    SUBJECT="autobkup-PREP SUMMARY: $thedate1 $RUN_TYPE"
    fileone="$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    echo -e "$SUBJECT\n" > "$outfile"
    echo -e "$thedate1  =  $thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
  elif [ "$type" == "summary" ]; then
    SUBJECT="autobkup-SUMMARY: $thedate1 $RUN_TYPE"
    fileone="$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    echo -e "$SUBJECT\n" > "$outfile"
    echo -e "$thedate1  =  $thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
    echo "SENDING"
  fi
  if [ -f "$outfile" ]; then
    if [ "$type" == "pre_error" ] || [ "$type" == "error" ]; then
      echo -e "============================\n" > "$_BANNERFILE"
      echo "$SUBJECT" >> "$_BANNERFILE"
      echo "$thedate1  =  $thedate2" >> "$_BANNERFILE"
      echo -e "============================\n" >> "$_BANNERFILE"
    fi
    if [ "$USE_EMAIL" == true ] && [ "$HAS_SWAKS" == true ] && [ ! -z "$_ALERTEMAIL" ] && [ -f "$_HOMEFOLDER/.swaksrc" ]; then
      scrape_swaks_config "$_HOMEFOLDER/"

      sudo swaks --from "$SWAKFROM" --h-From "$_SWAKHFROM" -s "$SWAKPROTO" -tls -a LOGIN --auth-user "$SWAKUSER" --auth-password "$SWAKPASS" --header "Subject: $SUBJECT" --body "$outfile" -t "$_ALERTEMAIL"
      echo "sent to $_ALERTEMAIL." | wall
    else
      #      mail -s "$SUBJECT" "$USER" < "$outfile"
      if [ "$type" == "pre_error" ] || [ "$type" == "error" ]; then
        cp -v "$outfile" "$drivepath/$type-$LOGSUFFIX"
        echo "$outfile"
      fi
    fi
  fi
}



#####################################################################
thedate="$(date +'%Y%m%d_T%H%M')"
thedate1="$(date +'%Y/%m/%d  %H:%M')"

SOURCE_SCRIPT=false
RUN_TYPE=false
PRE_CHECK=false
IGNORE_ERRS=false
USE_EMAIL=false


loadopts
loadrundata
#####################################################################
HAS_BLOCKID=true
HAS_MAIL=true
HAS_SWAKS=true

if ! hasfunct "blockid"; then
  HAS_BLOCKID=false
fi
echo "HAS_BLOCKID  $HAS_BLOCKID"
if ! hasfunct "mail"; then
  HAS_MAIL=false
fi
echo "HAS_MAIL  $HAS_MAIL"
if ! hasfunct "swaks"; then
  HAS_SWAKS=false
fi
echo "HAS_SWAKS  $HAS_SWAKS"
#####################################################################
BASELOCKPATH="${HOME}/log/autobackup/tmp/$RUN_TYPE"
RUNLOGPATH="${HOME}/log/autobackup/log/$RUN_TYPE"
RUNTMPPATH="${HOME}/log/autobackup/tmp/$RUN_TYPE"
if [ -e "/tmp/" ]; then
  #  if [ "$HAS_BLOCKID" == true ]; then
  BASELOCKPATH="/tmp/autobackup/abakup/$RUN_TYPE/$thedate"
  RUNLOGPATH="/var/log/autobackup/abakup/$RUN_TYPE/$thedate"
  RUNTMPPATH="/tmp/autobackup/abakup/$RUN_TYPE/$thedate"
  #  fi
fi
echo "HOME: ${HOME}"
echo "RUNTMPPATH: $RUNTMPPATH"

#####################################################################


if checklocked "$IGNORE_LOCKS" "$BASELOCKPATH" "$RUN_TYPE"; then
  lockfile=$(getlocked "$BASELOCKPATH" "$RUN_TYPE")
  locktime=$(cat "$lockfile")
  # send error mail with times of locked file, etc
  echo "LOCKED AT $locktime by $BASELOCKPATH/$RUN_TYPE.lock.txt"
  mailout "locked"
  exit
fi

setlocked "$BASELOCKPATH" "$RUN_TYPE" true "$thedate"


mkdir -p "$RUNLOGPATH"
mkdir -p "$RUNTMPPATH"

LOGSUFFIX="$RUN_TYPE-$thedate.txt"


rebuildtmpfiles "$RUNTMPPATH"



if [ "$HAS_BLOCKID" == true ]; then
  loadblockids
  loadmounts "$RUNTMPPATH" "cmount.txt"

  touch  "$RUNTMPPATH/mounted.txt"
  touch  "$RUNTMPPATH/unmounted.txt"

  findmounted "$RUNTMPPATH"
  automount "$RUNTMPPATH"

  cat "$RUNTMPPATH/unmounted.txt" > "$RUNTMPPATH/oldunmounted.txt"

  rebuildtmpfiles "$RUNTMPPATH"
  loadblockids

  loadmounts "$RUNTMPPATH" "cmount.txt"

  touch "$RUNTMPPATH/mounted.txt"
  touch "$RUNTMPPATH/unmounted.txt"
  findmounted "$RUNTMPPATH"
else
  loadmounts "$RUNTMPPATH" "mounted.txt"
fi

SOURCE_FOLDERPATH=false
ERROR_FAIL=false
verifydriveflags "$RUNTMPPATH"
findcopypaths

# If there was an error mounting/loading
if [ "$ERROR_FAIL" == true ] || [ "$PRE_ERROR_FAIL" == true ]; then
  thedate2="$(date +'%Y/%m/%d  %H:%M')"
  touch "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
  mailout "pre_error"
  exit 0
fi

ERRDUMP_FOLDERPATH="/tmp/autobackup/errdump"
ERRDUMP_FILEPATH="$ERRDUMP_FOLDERPATH/errdump-$thedate.txt"
mkdir -p "$ERRDUMP_FOLDERPATH"
echo "errdump: $ERRDUMP_FILEPATH"
echo "logpath: $RUNLOGPATH"

prefregstr="(?:\d+\/\d+\/\d+\s+\d+\:\d+\:\d+\s+\[\d+\]\s+)?"
if [ "$VALID_CHECK" == true ]; then
  PRE_ERROR_FAIL=false

  pyrun=$(python $SCRIPTDIR/raidcheck.py | tail -n 20)
  echo "..$pyrun"

  vlogpath=false
  for n in ${pyrun[@]}; do
    if echo "$n" | grep -qP "^\s*\-\s*logged in\:\s*"; then
      vlogpath=$(echo "$n" | grep -oP "\/.*$")
    fi
  done

  # throw an error
  if [ "$vlogpath" == false ]; then
    PRE_ERROR_FAIL=true
    ERROR_FAIL=true
    touch "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
    echo -e "ERROR: FAILURE OCCURRED IN VALIDATOR RUN:  '$vsummary'\n" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
    echo "$pyrun" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
    echo -e "\n\n------\n\n" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
    cat "$vsummary" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"

    echo "--b.2/1-- $m" >> "$ERRDUMP_FILEPATH"
    echo "$pyrun" >> "$ERRDUMP_FILEPATH"
  fi

  # Back up the validation logs on all possible drive targets
  if [ ! "$vlogpath" == false ]; then
    vbaselog=$(echo "$vlogpath" | grep -oP "^.*(?=\/md5vali\/\w+\/)")
    targetpaths=()
    for j in $(cat "$RUNTMPPATH/copypaths.txt"); do
      IFS=',' read -ra vals8 <<< "$j"    #Convert string to array
      targetdrivepath=${vals8[5]}
      targetpaths+=($targetdrivepath)
    done
    for p in ${targetpaths[@]}; do
#      targetdrivepath="${targetpaths["$p"]}"
      targetdrivepath="$p"

      mkdir -p "$targetdrivepath/logs/"
      touch "$tmpfile.2"
      rsync -hrltvvzWPSD --no-links --stats --no-compress --log-file="$tmpfile.2" "$vbaselog" "$targetdrivepath/logs/"

      parseresult=$(grepRSyncFailure "$prefregstr" "$tmpfile.2" "$RUNLOGPATH/prelog_errs-$LOGSUFFIX")
      if echo "$parseresult" | grep -qP "fail_\d+"; then
        PRE_ERROR_FAIL=true
        ERROR_FAIL=true
        if echo "$parseresult" | grep -qP "fail_1"; then
          echo "--a/1-- $vbaselog,$p" >> "$ERRDUMP_FILEPATH"
        fi
        if echo "$parseresult" | grep -qP "fail_2"; then
          echo "--a/2-- $vbaselog,$p" >> "$ERRDUMP_FILEPATH"
        fi
        grepRSyncFailure "$prefregstr" "$tmpfile.2" "$ERRDUMP_FILEPATH"
      fi
      rm -f "$tmpfile.2"
    done
  fi

  if [ ! "$vlogpath" == false ] && [ "$PRE_ERROR_FAIL" == false ]; then
    vdate=$(echo "$vlogpath" | grep -oP "(?<=master\-)\d+\-\d+(?=\.txt\s*$)")
    vpath=$(echo "$vlogpath" | grep -oP "^\/.*\/(?=master-[^\/]+\/[^\/]+\.txt\s*$)")
    vsummary="$vpath""md5vali-summary-$vdate.txt"

    for m in $(cat "$vsummary"); do
      if echo "$m" | grep -qP "(?:missing|conflicts)\s*\:\s*\d+"; then
        PRE_ERROR_FAIL=true
        ERROR_FAIL=true
        touch "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
        echo -e "ERROR: CONFLICT FOUND IN VALIDATOR RUN:  '$vsummary'\n" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
        cat "$vsummary" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"

        echo "--b/1-- $m" >> "$ERRDUMP_FILEPATH"
        cat "$vsummary" >> "$ERRDUMP_FILEPATH"
        break
      fi
#    rm -f "$RUNTMPPATH/rsynclog.txt"
    done
    vpresent="$vpath""master-$vdate/md5vali-present-$vdate.txt"
    if [ if "$vpresent" ]; then
      rm -f "$vpresent"
    fi
  fi
  if [ "$PRE_ERROR_FAIL" == true ]; then
    thedate2="$(date +'%Y/%m/%d  %H:%M')"
    mailout "pre_error"
    exit 0
  fi
  if [ -f "$vsummary" ]; then
    cat "$vsummary" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    echo -e "--------------------------\n" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
  fi
fi


if [ "$PRE_CHECK" == true ]; then
  PRE_ERROR_FAIL=false
  scanrsync true "$RUNTMPPATH/copypaths.txt" "$RUNLOGPATH/prelog_errs-$LOGSUFFIX" "$RUNTMPPATH/rsynclog.txt"
  rm -f "$RUNTMPPATH/rsynclog.txt"

  if [ "$PRE_ERROR_FAIL" == true ]; then
    thedate2="$(date +'%Y/%m/%d  %H:%M')"
    mailout "pre_error"
    exit 0
  fi
fi

if [ "$ERROR_FAIL" == true ]; then
  thedate2="$(date +'%Y/%m/%d  %H:%M')"
  mailout "error"
  exit 0
fi


df -h >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"


if [ "$PREP_ONLY" == true ]; then
  thedate2="$(date +'%Y/%m/%d  %H:%M')"
  mailout "prep_only"
  exit 0
fi


ERROR_FAIL=false
PRE_ERROR_FAIL=false
scanrsync false "$RUNTMPPATH/copypaths.txt" "$RUNLOGPATH/log_errs-$LOGSUFFIX" "$RUNLOGPATH/log_full-$LOGSUFFIX"
echo 'all rsync done'
rm -f "$RUNLOGPATH/log_full-$LOGSUFFIX.tmp"

thedate2="$(date +'%Y/%m/%d  %H:%M')"
if [ "$ERROR_FAIL" == true ]; then
  mailout "error"
else
  mailout "summary"
fi
rm -f "$RUNLOGPATH/log_shortened-$LOGSUFFIX"

#####################################################################

##autounmount "$RUNTMPPATH"


setlocked "$BASELOCKPATH" "$RUN_TYPE" false "$thedate"

echo
echo "BACKUP RAN SUCCESSFULLY"
exit 0



# catch notifications/errors
#                 - note: high overwrite arate!  > 40%
#                 - err: no md5 matches

# launch validator beforehand?
# run if conflicts occur? what about edited files???
#     run validator tuesday nights?
#     backup thurs nights IIF:    no conflicts, or at least "okayed" conflicts
#     validator pre-run as check?

#
#  https://serverfault.com/questions/348482/how-to-remove-invalid-characters-from-filenames
#  https://unix.stackexchange.com/questions/109747/identify-files-with-non-ascii-or-non-printable-characters-in-file-name

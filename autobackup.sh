#!/bin/bash
# imports certain functions when running as non-user root
export PATH=$PATH:/sbin

IFS=$'\n'

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`


hasfunct() {
  testfn="$1"
  if [ "$testfn" == "blockid" ]; then
    $(blkid > /dev/null 2>&1)
    if [ "$?" -eq 127 ]; then
      false
    else
      true
    fi
  elif [ "$testfn" == "mdadm" ]; then
    $(mdadm > /dev/null 2>&1)
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


echo "Running: $SCRIPTPATH"
OPTS=`getopt -o vh: --long verbose,mountonly,force,help,email,dryrun,vcheck,preponly,verbose,sourcescript:,runtype: -n 'parse-options' -- "$@"`

if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi

source "$SCRIPTDIR/config/autobackup_config.sh"
source "$SCRIPTDIR/bash_libs/scrape_swaks.sh"
source "$SCRIPTDIR/bash_libs/lock_and_tmp_files.sh"
source "$SCRIPTDIR/bash_libs/parse_output.sh"
source "$SCRIPTDIR/bash_libs/handle_mounts.sh"

# https://unix.stackexchange.com/questions/102211/rsync-ignore-owner-group-time-and-perms

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

loadopts() {
  echo "$OPTS"
  eval set -- "$OPTS"

  VERBOSE=false
  HELP=false
  VALID_CHECK=false
  PREP_ONLY=false
  IGNORE_LOCKS=false
  BACKUP_VERBOSE=false
  MOUNT_ONLY=false

  while true; do
   case "$1" in
-v | --verbose ) VERBOSE=true; shift ;;
-h | --help )    HELP=true; shift ;;
--runtype )   RUN_TYPE="$2"; shift 2 ;;
--sourcescript )  SOURCE_SCRIPT="$2"; shift 2 ;;
--force )   IGNORE_LOCKS=true; shift ;;
--dryrun ) DRY_RUN=true; shift ;;
--email )   USE_EMAIL=true; shift ;;
--vcheck )  VALID_CHECK=true; shift ;;
--preponly )  PREP_ONLY=true; shift ;;
--verbose )  BACKUP_VERBOSE=true; shift ;;
--mountonly ) MOUNT_ONLY=true; IGNORE_LOCKS=true; shift ;;
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
  sourcematchpath="$1"

  if [[ $SCRIPTPATH == $sourcematchpath* ]] && [ "$SOURCE_SCRIPT" == false ]; then
    true
  elif [ ! "$SOURCE_SCRIPT" == false ]; then
    if [[ $SOURCE_SCRIPT == $sourcematchpath* ]]; then
      true
#    elif [[ "$sourcematchpath" == "/drives/c" ]] && [[ "$HOME" == "/home/mobaxterm" ]] && [[ "$SCRIPTPATH" == /home/* ]]; then
#      true
    else
      false
    fi
  else
#    if [[ "$sourcematchpath" == "/drives/c" ]] && [[ "$HOME" == "/home/mobaxterm" ]] && [[ "$SCRIPTPATH" == /home/* ]]; then
#      true
#    else
      false
#    fi
  fi
}
#####################################
findcopypaths() {
  runtmppath="$1"
  drivepathfile="$2"
  copypathfile="$3"
  echo "load drives: $drivepathfile"

  touch "$copypathfile"
  echo ""
  for j in $(cat "$drivepathfile"); do
    IFS=',' read -ra vals5 <<< "$j"    #Convert string to array

    opath=${vals5[0]}
    path=${vals5[1]}
    type=${vals5[2]}
    driveflag=${vals5[3]}


    backupflags=()
    if sourcematch "$path"; then
        flagname="_BACKUP"$(echo "$driveflag" | grep -oP "(?<=_DRIVE)FLAG_\w+_")
        echo "$flagname"
        for k in $(ls -1 "$SCRIPTDIR/$_AUTOBACKUPINFOFOLDER"); do
            if [ "$k" == "$flagname.txt" ]; then
                backupflags+=($flagname)
            fi
        done
    fi

    for back in ${backupflags[@]}; do
      backfile="$back"

      if [ -f "$SCRIPTDIR/$_AUTOBACKUPINFOFOLDER/$backfile.txt" ]; then
        for m in $(cat "$SCRIPTDIR/$_AUTOBACKUPINFOFOLDER/$backfile.txt"); do

          if echo "$m" | grep -qP "^\s*\w+,"; then

            #      $runname,$copytype,$sourceflag,$sourcepath,$targetflag,$targetpath
            IFS=',' read -ra vals6 <<< "$m"    #Convert string to array
            runname=${vals6[0]}
            copytype=${vals6[1]}
            sourceflag=${vals6[2]}
            sourcepath=${vals6[3]}
            targetflag=${vals6[4]}
            targetpathM=${vals6[5]}
            targetpath=$(echo "$targetpathM" | sed -e "s/[]//g")

            if [ "$RUN_TYPE" != "$runname" ]; then
              continue
            fi

            DEST_FOUND=false
            SOURCE_FOUND=false
            SOURCE_MATCHES_SELF=false

            if [ "$RUN_TYPE" == "$runname" ]; then
              if [ "$driveflag" == "$sourceflag" ]; then

                SOURCE_FOUND=true
                if sourcematch "$path"; then
                  SOURCE_MATCHES_SELF=true

                  for n in $(cat "$drivepathfile"); do
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
                echo "$runname,$copytype,$drivepath,$sourceflag,$sourcepath,$targetdrivepath,$targetflag,$targetpath" >> "$RUNTMPPATH/copypaths.txt"
                echo "$runname,$copytype,$drivepath,$sourceflag,$sourcepath,$targetdrivepath,$targetflag,$targetpath"

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
  echo ""
}
scanrsync() {
  testrun=$1
  pathsfile="$2"                  # $RUNTMPPATH/copypaths.txt
  tmperrfile="$3"                 # $RUNLOGPATH/prelog_errs-$LOGSUFFIX
  tmplog="$4"                     # $RUNTMPPATH/rsynclog.txt
  errdump="$ERRDUMP_FILEPATH"        # $ERRDUMP_FILEPATH

  if [ ! -s "$pathsfile" ]; then
    echo "No paths found!"
    return
  fi

  rcount=-1
  for j in $(cat "$pathsfile"); do
    IFS=',' read -ra vals8 <<< "$j"    #Convert string to array

    runname=${vals8[0]}
    copytype=${vals8[1]}
    drivepath=${vals8[2]}
    sourceflag=${vals8[3]}
    sourcepath=${vals8[4]}
    targetdrivepath=${vals8[5]}
    targetflag=${vals8[6]}
    targetpath=${vals8[7]}

    mkdir -p "$targetdrivepath/$targetpath"
    LOOP_ERROR_FAIL=false

    rcount=$((rcount+1))
    if [ "$testrun" == true ]; then
      errdumpltr="c"
    else
      errdumpltr="e"
    fi

    rm -f "$tmperrfile.tmp"
    touch "$tmperrfile.tmp"
    echo -e "\n--------- $sourcepath ----------\n" >> "$tmperrfile.tmp"
    rm -f "$tmplog"
    rm -f "$tmperrfile.tmp2"

    echo '-----------------------------------------------------'
    echo '-----------------------------------------------------'
    if [ -e "$drivepath/$sourcepath" ] && [ -e "$targetdrivepath/$targetpath" ]; then

      touch "$tmplog"
      echo -e "\n--------- $sourcepath ----------\n"
#     c, D, z
#      basev="-hrltzOWPSD"      # try  --inplace instead of -S spare?  could result in bad files(?), but would greatly improve harddrive lifespan
      basev="-hrtOWSD"
      extend="--no-links --stats --no-compress --exclude-from '$SCRIPTDIR/config/autobackup_excludes.txt' "
      if [ -d "$drivepath/$sourcepath" ]; then
        if [ ! "$copytype" == "drop" ]; then
          extend+="--delete --delete-after "
        fi
      fi

      if [ "$testrun" == true ]; then
        extend+="--dry-run "
      fi
      if [ "$BACKUP_VERBOSE" == true ]; then
        basev+="vv"
      fi

      echo "rsync $basev $extend '$drivepath/$sourcepath' '$targetdrivepath/$targetpath'"
      eval "rsync $basev $extend --log-file='$tmplog' '$drivepath/$sourcepath' '$targetdrivepath/$targetpath' 2>'$tmperrfile.tmp2'"

      echo "rsync completed."
      touch "$tmplog"

    elif [ ! -e "$drivepath/$sourcepath" ]; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo "**** ERRR 1,$drivepath/$sourcepath"
      echo -e "ERROR: PATH '$drivepath/$sourcepath' NOT FOUND for source drive '$sourceflag'\n" >> "$tmperrfile.tmp"
      echo -e "--------------------------\n" >> "$tmperrfile.tmp"

      echo "--$errdumpltr/1-- $sourcepath : $j" >> "$errdump"
      echo "-- -- -- $drivepath/$sourcepath" >> "$errdump"
    elif [ ! -e "$targetdrivepath/$targetpath" ]; then

      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo "**** ERRR 2"
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


    if [ "$?" == "0" ] && [ ! -s "$tmperrfile.tmp2" ]; then
      echo "Successful rsync."
    else
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo "**** ERRR 3,$?,$tmperrfile.tmp2"
      if [ ! -s "$tmperrfile.tmp2" ]; then echo "XX"; fi

      errlabel=$(getrsyncerrcode "$?")
      echo -e "------ $? : $errlabel : $sourcepath ------\n" >> "$tmperrfile.tmp"
      ################################################ ERRORED HERE, e/3
      echo "--$errdumpltr/3-- $j" >> "$tmperrfile.tmp"
      echo "-- -- -- $? : $errlabel : $sourcepath" >> "$tmperrfile.tmp"
      echo "--$errdumpltr/3-- $j" >> "$errdump"
      echo "-- -- -- $? : $errlabel : $sourcepath" >> "$errdump"
    fi

    parseresult=$(grepRSyncFailure "$tmplog" "$tmperrfile.tmp")
    if echo "$parseresult" | grep -qP "fail_\d+"; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo "**** ERRR 4"

      echo "--$errdumpltr/4-- $sourcepath : $j" >> "$tmperrfile.tmp"
      grepRSyncFailure "$tmplog" "$tmperrfile.tmp"
      echo "--$errdumpltr/4-- $sourcepath : $j" >> "$errdump"
      grepRSyncFailure "$tmplog" "$errdump"
      echo "Errors detected."
    fi
    parseresult2=$(grepRSyncFailure "$tmplog" "$tmperrfile.tmp2")
    if echo "$parseresult2" | grep -qP "fail_\d+"; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo "**** ERRR 5"

      echo "--$errdumpltr/5-- $sourcepath : $j" >> "$tmperrfile.tmp2"
      grepRSyncFailure "$tmplog" "$tmperrfile.tmp2"
      echo "--$errdumpltr/5-- $sourcepath : $j" >> "$errdump"
      grepRSyncFailure "$tmplog" "$errdump"
      echo "$tmperrfile.tmp2" >> "$errdump"
      echo "Errors detected."
    fi
    ############### DIFFERS AT THIS POINT
    if [ "$copytype" == "drop" ] && [ "$testrun" == false ] && [ "$ERROR_FAIL" == false ]; then
      for x in $(find "$drivepath/$sourcepath" -type f -not -path "*/.sync/*"); do
        if echo "$x" | grep -qiP "\.(jpe?g|png|gif|mp3|mp4|zip|rar|txt|mov|wav|webm|jpw?g_?large|csv|js|mkv|ogg|pdf|webp|jar|html|epub|csv|m4a)$"; then
          rm -f "$x"
        else
          echo "skip drop: $x"
          touch "$RUNLOGPATH/log_skipdelete-$LOGSUFFIX"
          echo "$x" >> "$RUNLOGPATH/log_skipdelete-$LOGSUFFIX"
        fi
      done
      find "$drivepath/$sourcepath/" -type d -mindepth 2 -depth -exec rmdir -v {} \;# 2>/dev/null
    fi

    if [ "$testrun" == false ]; then
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_deletes-$LOGSUFFIX"
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_copies-$LOGSUFFIX"
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_folders-$LOGSUFFIX"
      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_matches-$LOGSUFFIX"
      PRESUFF="(?:[\w\:\s\/]+\[\d+\]\s+)?"
      grep -P "^$PRESUFF\s*\*?deleting\s+.*" "$tmplog" >> "$RUNLOGPATH/log_deletes-$LOGSUFFIX"
      grep -P "^$PRESUFF\s*>f\+{9,10}\s+\S.*[^\s\/]\s*$" "$tmplog" >> "$RUNLOGPATH/log_copies-$LOGSUFFIX"
      grep -P "^$PRESUFF\s*cd\+{9,10}\s+\S.*\/\s*$" "$tmplog" >> "$RUNLOGPATH/log_folders-$LOGSUFFIX"
#      grep -P "^$PRESUFF\s*\S.*\s+is uptodate\s*$" "$tmplog" >> "$RUNLOGPATH/log_matches-$LOGSUFFIX"

      echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
      parsersync "$tmplog" "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    fi
    ###############

    if [ -f "$tmplog" ]; then
      cp "$tmplog" "$tmplog.$rcount"
    fi
    if [ "$LOOP_ERROR_FAIL" == true ]; then
      if [ -f "$tmperrfile.tmp" ]; then
        cat "$tmperrfile.tmp" >> "$tmperrfile"
      fi
      if [ -f "$tmperrfile.tmp2" ]; then
        cat "$tmperrfile.tmp2" >> "$tmperrfile"
      fi
    fi
    rm -f "$tmperrfile.tmp"
  done
  if [ "$ERROR_FAIL" == true ] || [ "$LOOP_ERROR_FAIL" == true ]; then
      echo "Errors found!  Feedback saved at:"
      if [ -f "$tmperrfile.tmp" ]; then echo "$tmperrfile.tmp"; fi
      if [ -f "$tmperrfile" ]; then echo "$tmperrfile"; fi
      if [ -f "$errdump" ]; then echo "$errdump"; fi
      echo ""
  fi
}
mailout() {
  type="$1"
  outfile="$RUNLOGPATH/log_tmp-$LOGSUFFIX"
  rm -f "$outfile"

  SUBJECT=""
  if [ "$type" == "locked" ]; then
    mkdir -p "$RUNLOGPATH"
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
    fileone="$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    fileone2="$RUNLOGPATH/log_errs-$LOGSUFFIX"
    echo -e "$SUBJECT\n" > "$outfile"
    echo -e "$thedate1  =  $thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
    echo "--------------------" >> "$outfile"
    echo "--------------------" >> "$outfile"
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
      echo "sent to $_ALERTEMAIL."
    else
      #      mail -s "$SUBJECT" "$USER" < "$outfile"
      if [ "$type" == "pre_error" ] || [ "$type" == "error" ]; then
        cp -fv "$outfile" "$HOME/$type-$LOGSUFFIX"
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
DRY_RUN=false
IGNORE_ERRS=false
USE_EMAIL=false

echo "Loading Options"
loadopts
echo "Check Run Data"
loadrundata
#####################################################################
HAS_BLOCKID=true
HAS_MAIL=true
HAS_MDADM=true
HAS_SWAKS=true

echo "Check functions"

if ! hasfunct "mdadm"; then
  HAS_MDADM=false
fi
echo "HAS_MDADM  $HAS_MDADM"
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
  BASELOCKPATH="/tmp/autobackup/abakup/$RUN_TYPE/"
  RUNLOGPATH="/var/log/autobackup/abakup/$RUN_TYPE/$thedate"
  RUNTMPPATH="/tmp/autobackup/abakup/$RUN_TYPE/$thedate"
  #  fi
fi
echo "HOME: ${HOME}"
echo "RUNTMPPATH: $RUNTMPPATH"

LOGSUFFIX="$RUN_TYPE-$thedate.txt"

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

if [ "$MOUNT_ONLY" == true ]; then
  if [ "$HAS_BLOCKID" == true ]; then
    exit 0;
  else
    echo "FAILURE TO RUN AUTOMOUNTING; NO BLOCKID COMMAND FOUND"
    exit 0;
  fi
fi



SOURCE_FOLDERPATH=false
ERROR_FAIL=false

builddrivepaths "$RUNTMPPATH" "$RUNTMPPATH/drives.txt"
findcopypaths "$RUNTMPPATH" "$RUNTMPPATH/drives.txt" "$RUNTMPPATH/copypaths.txt"

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
      targetdrivepath="$p"

      mkdir -p "$targetdrivepath/logs/"
      touch "$tmpfile.x2"

      # Save the validation logs
      rsync -hrltvvzWPSD --no-links --stats --no-compress --log-file="$tmpfile.x2" "$vbaselog" "$targetdrivepath/logs/"

      parseresult=$(grepRSyncFailure "$tmpfile.x2" "$RUNLOGPATH/prelog_errs-$LOGSUFFIX")
      if echo "$parseresult" | grep -qP "fail_\d+"; then
        PRE_ERROR_FAIL=true
        ERROR_FAIL=true
        if echo "$parseresult" | grep -qP "fail_1"; then
          echo "--a/1-- $vbaselog,$p" >> "$ERRDUMP_FILEPATH"
        fi
        if echo "$parseresult" | grep -qP "fail_2"; then
          echo "--a/2-- $vbaselog,$p" >> "$ERRDUMP_FILEPATH"
        fi
        grepRSyncFailure "$tmpfile.x2" "$ERRDUMP_FILEPATH"
      fi
      rm -f "$tmpfile.x2"
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
    summaryout="$RUNLOGPATH/log_summarycheck-$LOGSUFFIX"
    rm -fv "$summaryout"
    touch "$summaryout"
    parsevalidsummary "$vsummary" "$summaryout"
    echo -e "--------------------------\n" >> "$summaryout"
    cat "$summaryout" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
  fi
fi


if [ "$DRY_RUN" == true ]; then
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
if [ "$HAS_MDADM" == true ]; then
  echo "" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
  mdadm -D /dev/md127 >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
  echo "" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
  cat /proc/mdstat >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
fi

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
echo
echo "Logs saved at:"
echo "$RUNLOGPATH"
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

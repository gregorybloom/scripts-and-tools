#!/bin/bash
IFS=$'\n'

OPTS=`getopt -o vh: --long verbose,force,help,email,precheck,vcheck,preponly,runtype: -n 'parse-options' -- "$@"`
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi

source "config/autobackup_config.sh"

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
checklocked() {
  lockedrunname=$1
  if [ -f "$BASELOGPATH/$lockedrunname.lock.txt" ]; then
    if [ "$IGNORE_LOCKS" == true ]; then
      rm -f "$BASELOGPATH/$lockedrunname.lock.txt"
      false
    else
      true
    fi
  else
    false
  fi
}
getlocked() {
  lockedrunname=$1
  echo "$BASELOGPATH/$lockedrunname.lock.txt"
}
setlocked() {
  lockedrunname=$1
  setlocked=$2
  time=$3
  if [ "$setlocked" == true ]; then
    if [ ! -d "$BASELOGPATH/" ]; then
      mkdir -p "$BASELOGPATH/"
    fi
    if [ ! -f "$BASELOGPATH/$lockedrunname.lock.txt" ]; then
      echo "$time" > "$BASELOGPATH/$lockedrunname.lock.txt"
    fi
  else
    if [ -f "$BASELOGPATH/$lockedrunname.lock.txt" ]; then
      rm -f "$BASELOGPATH/$lockedrunname.lock.txt"
    fi
  fi
}

rebuildtmpfiles() {
  if [ ! -d "$RUNTMPPATH" ]; then
   mkdir -p "$RUNTMPPATH"
 fi
 tmpfiles=("blkid.txt" "unmounted.txt" "cmount.txt" "mounted.txt" "dmount.txt" "copypaths.txt" "rsynclog.txt")
 for p in ${!tmpfiles[@]}; do
  if [ -f "$RUNTMPPATH/${tmpfiles["$p"]}" ]; then
    rm -f "$RUNTMPPATH/${tmpfiles["$p"]}"
  fi
done
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
loadblockids() {
  for a in $(blkid); do
    # Unable to start 'blkid': The specified file was not found.
    if echo "$a" | grep -qP "^\/dev\/\w+\:\sLABEL=\"[\w\-\s]+\""; then
      uuid=$(echo "$a" | grep -oP "(?<=\sUUID=\")[\w\-]+(?=\")")
      type=$(echo "$a" | grep -oP "(?<=\sTYPE=\")[\w\-]+(?=\")")
      path=$(echo "$a" | grep -oP "^[^\:\s]+(?=\:)")
      label=$(echo "$a" | grep -oP "(?<=\sLABEL=\")[^\"]+(?=\")")
      echo "$uuid,$type,$path,$label" >> "$RUNTMPPATH/blkid.txt"
    fi
  done
}
loadmounts() {
  filename="$1"
  for b in $(mount); do
    if echo "$b" | grep -qP "^(?:[A-Z]\:)?[\w\-\/]* on \/[^\s]+ type \w+ \([^\(\)]+\)$"; then
     opath=$(echo "$b" | grep -oP "^(?:(?<=\w\:)|(?<=))[^\s]+(?= on )")
     dpath=$(echo "$b" | grep -oP "(?<= on )\/[^\s]+(?= type)")
     dtype=$(echo "$b" | grep -oP "(?<= type )\w+(?= \([^\(\)]+\)$)")
     echo "$opath,$dpath,$dtype" >> "$RUNTMPPATH/$filename"
   fi
 done
}
loadopts() {
  echo "$OPTS"
  eval set -- "$OPTS"

  VERBOSE=false
  HELP=false
  VALID_CHECK=false
  PREP_ONLY=false

  while true; do
   case "$1" in
     -v | --verbose ) VERBOSE=true; shift ;;
-h | --help )    HELP=true; shift ;;
--runtype )   RUN_TYPE="$2"; shift 2 ;;
--force )   IGNORE_LOCKS=true; shift ;;
--precheck ) PRE_CHECK=true; shift ;;
--email )   USE_EMAIL=true; shift ;;
--vcheck )  VALID_CHECK=true; shift ;;
--preponly )  PREP_ONLY=true; shift ;;
-- ) shift; break ;;
* ) break ;;
esac
done

echo VERBOSE=$VERBOSE
echo HELP=$HELP
echo RUN_TYPE=$RUN_TYPE
}
loadrundata() {
  if [ "$RUN_TYPE" == false ]; then
    exit 1;
  fi

}
#####################################
findmounted() {
  for i in $(cat "$RUNTMPPATH/blkid.txt"); do
    IFS=',' read -ra vals <<< "$i"    #Convert string to array
    uuid=${vals[0]}
    type=${vals[1]}
    path=${vals[2]}
    label=${vals[3]}
    MOUNT_FOUND=false
    for j in $(cat "$RUNTMPPATH/cmount.txt"); do
      IFS=',' read -ra vals2 <<< "$j"    #Convert string to array
      opath=${vals2[0]}
      dpath=${vals2[1]}
      dtype=${vals2[2]}
      #      echo "$uuid, $type==$dtype,  $opath==$path"
      if [[ "$opath" == "$path" ]]; then
        #       if [[ "$type" == "$dtype" ]]; then
        echo "$opath,$dpath,$dtype" >> "$RUNTMPPATH/mounted.txt"
        #        echo "mount,$opath,$dpath,$dtype"
        MOUNT_FOUND=true
        break
        #       fi
      fi
    done
    if [ "$MOUNT_FOUND" == false ]; then
     echo "$uuid,$type,$path,$label" >> "$RUNTMPPATH/unmounted.txt"
     #      echo "nomount,$uuid,$type,$path,$label"
   fi
 done
}
autounmount() {
  for i in $(cat "$RUNTMPPATH/newmounted.txt"); do
      IFS=',' read -ra vals2 <<< "$j"    #Convert string to array
      thetype=${vals2[0]}
      opath=${vals2[1]}
      dpath=${vals2[2]}
      umount -vl "$dpath"
  done
}
automount() {
  if [ ! -f "$RUNTMPPATH/newmounted.txt" ]; then
    rm -f "$RUNTMPPATH/newmounted.txt"
  fi
  touch "$RUNTMPPATH/newmounted.txt"

  mountnames=()
  for i in $(ls -l "/media/"); do
    if echo "$i" | grep -qP "d[\w\-\.]+\s*\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\d+\s+(?:\d+\:)?\d+\s+\w+\s*$"; then
      mname=$(echo "$i" | grep -oP "(?<=\s)\w+\s*$")
      mountnames+=($mname)
    fi
  done
  for j in $(cat "$RUNTMPPATH/unmounted.txt"); do
    IFS=',' read -ra vals3 <<< "$j"    #Convert string to array
    uuid=${vals3[0]}
    type=${vals3[1]}
    path=${vals3[2]}
    label=${vals3[3]}
    targetname=$(echo "$label" | tr '[:upper:]' '[:lower:]')
    ############## ELIMINATE SPACES FROM $TARGETNAME !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    if [ ! -d "/media/$targetname" ]; then
      sudo mkdir -v "/media/$targetname"
    fi

    if [ "$type" == "ntfs" ]; then
      #     echo "mount -t auto $path /media/$targetname"
      "$RUNTMPPATH/newmounted.txt"

      sudo mount -t "auto" "$path" "/media/$targetname"
      echo "auto,$path,/media/$targetname" >> "$RUNTMPPATH/newmounted.txt"
    fi
  done
}
verifydriveflags() {
  mv "$RUNTMPPATH/mounted.txt" "$RUNTMPPATH/mounted.tmp.txt"
  touch "$RUNTMPPATH/mounted.txt"
  for j in $(cat "$RUNTMPPATH/mounted.tmp.txt"); do
    IFS=',' read -ra vals4 <<< "$j"    #Convert string to array
    opath=${vals4[0]}
    path=${vals4[1]}
    type=${vals4[2]}
    DRIVE_FLAG=false
    for k in $(ls -l "$path"); do
#      echo "$k," $(echo "$k" | grep -oP "^\-[\w\-\.\+]+\s*\d+\s+[\w\+]+\s+[\w\+]+\s+\d+\s+\w+\s+\d+\s+(?:\d+\:)?\d+\s+_DRIVEFLAG_\w+_\.txt\s*$")
      if echo "$k" | grep -qP "^\-[\w\-\.+]+\s*\d+\s+[\w\+]+\s+[\w\+]+\s+\d+\s+\w+\s+\d+\s+(?:\d+\:)?\d+\s+_DRIVEFLAG_\w+_\.txt\s*$"; then
        DRIVE_FLAG=$(echo "$k" | grep -oP "(?<=\s)_DRIVEFLAG_\w+_(?=\.txt\s*$)")
 #       echo "        2- $DRIVE_FLAG"
        break
      fi
    done
    if [ "$DRIVE_FLAG" == false ]; then
      continue
    fi
    echo "$opath,$path,$type,$DRIVE_FLAG" >> "$RUNTMPPATH/mounted.txt"
    #    echo "$opath,$path,$type,$driveflag"
  done
}
findcopypaths() {
  touch "$RUNTMPPATH/copypaths.txt"
  for j in $(cat "$RUNTMPPATH/mounted.txt"); do
    IFS=',' read -ra vals5 <<< "$j"    #Convert string to array

    opath=${vals5[0]}
    path=${vals5[1]}
    type=${vals5[2]}
    driveflag=${vals5[3]}
    backupflags=()

    for k in $(ls -l "$path"); do
      if echo "$k" | grep -qP "^\-[\w\-\.\+]+\s*\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\d+\s+(?:\d+\:)?\d+\s+_BACKUPFLAG_\w+_\.txt\s*$"; then
        bkupflag=$(echo "$k" | grep -oP "(?<=\s)_BACKUPFLAG_\w+_(?=\.txt\s*$)")
        backupflags+=($bkupflag)
      fi
    done

    for back in ${!backupflags[@]}; do
      backfile="${backupflags["$back"]}"

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
            targetpath=${vals6[5]}

            DEST_FOUND=false
            SOURCE_FOUND=false

            if [ "$RUN_TYPE" == "$runname" ]; then
              if [ "$driveflag" == "$sourceflag" ]; then
                SOURCE_FOUND=true
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
              if [ "$DEST_FOUND" == true ]; then
                drivepath=$(echo "$path")
                echo "$runname,$copystep,$drivepath,$sourceflag,$sourcepath,$targetdrivepath,$targetflag,$targetpath" >> "$RUNTMPPATH/copypaths.txt"
                echo "$runname,$copystep,$drivepath,$sourceflag,$sourcepath,$targetdrivepath,$targetflag,$targetpath"
              elif [ "$SOURCE_FOUND" == true ]; then
                echo "destination drive '$targetflag' not found"
                ERROR_FAIL=true
                touch "$RUNLOGPATH/log_errs-$LOGSUFFIX"
                echo -e "ERROR: DESTINATION DRIVE '$targetflag' NOT FOUND\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
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
greprsynclines() {
  pref="^\d+\/\d+\/\d+\s+\d+\:\d+\:\d+\s+\[\d+\]\s+"

  nopermission=("^rsync\:.*\: Permission denied \(\d+\)\s*$")
  notpermitted=("^rsync\:.*\: Operation not permitted \(\d+\)\s*$")
  reporting=()
  reporting+=("^(?:sent|total)\s*(?:size is|\: matches=)?\s*\d+")
  reporting+=("rsync error\:.*$")
  drek=()
}


readrsyncline() {
  rline=$1
  if echo "$rline" | grep -qP "^\d+\/\d+\/\d+\s+\d+\:\d+\:\d+\s+\[\d+\]\s+"; then
    prefstr=$(echo "$rline" | grep -oP "^\d+\/\d+\/\d+\s+\d+\:\d+\:\d+\s+\[\d+\]\s+")
    preflen=$((1+${#prefstr}))
    rline=$(echo "$rline" | cut -c "$preflen-")
  fi

  if echo "$rline" | grep -qP "^rsync\:.*\: Permission denied \(\d+\)\s*$"; then
    echo "nopermission"
  elif echo "$rline" | grep -qP "^rsync\:.*\: Operation not permitted \(\d+\)\s*$"; then
    echo "notpermitted"
  elif echo "$rline" | grep -qP "^(?:sent|total)\s*(?:size is|\: matches=)?\s*\d+"; then
    echo "reporting"
  elif echo "$rline" | grep -qP "^rsync error\:.*$"; then
    echo "reporting"
  elif echo "$rline" | grep -qP "^delta-transmission disabled.*/s*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^(?:generate_files|recv_files|send_files) (?:finished|phase=\d+)/s*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^sending incremental file list/s*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^deleting in \.\s*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^delete_in_dir\(\.\)\s*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^deleting\s+.*\/\s*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^(?:recv_generator|recv_files|send_files|recv_file_name|delete_item)\(.*\)\s*(?:\w+=\d+\s*)*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^(?:server_recv)\(.*\)\s*(?:\w*\s*\w+=\d+\s*)*$"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^\[generator]\s+.*"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^\[sender]\s+.*"; then
    echo "drek"
  elif echo "$rline" | grep -qP "^deleting\s+.*"; then
    echo "deleted"
  elif echo "$rline" | grep -qP "^\>f\+{9,10}\s+\S.*[^\s\/]\s*$"; then
    echo "copied"
  elif echo "$rline" | grep -qP "^cd\+{9,10}\s+\S.*[^\s\/]\s*$"; then
    echo "folder"
  else
    echo "misc"
  fi

}
getrsyncerrcode() {
  num="$1"
  if [ "$num" == 1 ]; then
    echo "Syntax or usage error"
  elif [ "$num" == 2 ]; then
    echo "Protocol incompatibility"
  elif [ "$num" == 3 ]; then
    echo "Errors selecting input/output files, dirs"
  elif [ "$num" == 4 ]; then
    echo "Requested action not supported"
  elif [ "$num" == 5 ]; then
    echo "Error starting client-server protocol"
  elif [ "$num" == 6 ]; then
    echo "Daemon unable to append to log-file"
  elif [ "$num" == 10 ]; then
    echo "Error in socket I/O"
  elif [ "$num" == 11 ]; then
    echo "Error in file I/O"
  elif [ "$num" == 12 ]; then
    echo "Error in rsync protocol data stream"
  elif [ "$num" == 13 ]; then
    echo "Errors with program diagnostics"
  elif [ "$num" == 14 ]; then
    echo "Error in IPC code"
  elif [ "$num" == 20 ]; then
    echo "Received SIGUSR1 or SIGINT"
  elif [ "$num" == 21 ]; then
    echo "Some error returned by waitpid()"
  elif [ "$num" == 22 ]; then
    echo "Error allocating core memory buffers"
  elif [ "$num" == 23 ]; then
    echo "Partial transfer due to error"
  elif [ "$num" == 24 ]; then
    echo "Partial transfer due to vanished source files"
  elif [ "$num" == 25 ]; then
    echo "The --max-delete limit stopped deletions"
  elif [ "$num" == 30 ]; then
    echo "Timeout in data send/receive"
  elif [ "$num" == 35 ]; then
    echo "Timeout waiting for daemon connection"
  fi
}
mailout() {
  type="$1"
  outfile="$RUNLOGPATH/log_tmp-$LOGSUFFIX"
  rm -f "$outfile"
  SUBJECT=""
  if [ "$type" == "locked" ]; then
    SUBJECT="autobkup-LOCKED: $thedate $RUN_TYPE"
    echo "LOCKED AT $locktime by $BASELOGPATH/$RUN_TYPE.lock.txt" > "$outfile"
    echo "\n$thedate\n" >> "$outfile"
  elif [ "$type" == "pre_error" ]; then
    SUBJECT="autobkup-PRE_ERROR: $thedate $RUN_TYPE"
    fileone="$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
    echo "$SUBJECT\n" > "$outfile"
    echo "\n$thedate\n$thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
    if [ "$ERROR_FAIL" == true ]; then
      fileone2="$RUNLOGPATH/log_errs-$LOGSUFFIX"
      cat "\n==========\n\n" >> "$outfile"
      cat "$fileone2" >> "$outfile"
    fi
  elif [ "$type" == "error" ]; then
    SUBJECT="autobkup-ERROR: $thedate $RUN_TYPE"
    fileone="$RUNLOGPATH/log_errs-$LOGSUFFIX"
    fileone2="$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    echo "$SUBJECT\n" > "$outfile"
    echo "\n$thedate\n$thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
    cat "$fileone2" >> "$outfile"
  elif [ "$type" == "summary" ]; then
    SUBJECT="autobkup-SUMMARY: $thedate $RUN_TYPE"
    fileone="$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    echo "$SUBJECT\n" > "$outfile"
    echo "\n$thedate\n$thedate2\n" >> "$outfile"
    cat "$fileone" >> "$outfile"
  fi
  if [ -f "$outfile" ]; then
    if [ "$type" == "pre_error" ] || [ "$type" == "error" ]; then
      echo -e "============================\n" > "$_BANNERFILE"
      echo "$SUBJECT" >> "$_BANNERFILE"
      echo "$thedate\n$thedate2" >> "$_BANNERFILE"
      echo -e "============================\n" >> "$_BANNERFILE"
    fi
    if [ "$USE_EMAIL" == true ] && [ "$HAS_SWAKS" == true ] && [ ! -z "$_ALERTEMAIL" ]; then
      swaks --header "Subject: $SUBJECT" --body "$fileone" -t "$_ALERTEMAIL"
    else
      #      mail -s "$SUBJECT" "$USER" < "$outfile"
      if [ "$type" == "pre_error" ] || [ "$type" == "error" ]; then
        cp -v "$outfile" "$drivepath/$type-$LOGSUFFIX"
      fi
    fi
  fi
}





#####################################################################
thedate="$(date +'%Y%m%d_T%H%M')"

RUN_TYPE=false
PRE_CHECK=false
IGNORE_ERRS=false
USE_EMAIL=false

BASELOGPATH="${HOME}/log/backup"

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
if [ -e "/var/log/" ]; then
  #  if [ "$HAS_BLOCKID" == true ]; then
  BASELOGPATH="/var/log/backup"
  #  fi
fi
#####################################################################


if checklocked "$RUN_TYPE"; then
  lockfile=$(getlocked "$RUN_TYPE")
  locktime=$(cat "$lockfile")
  # send error mail with times of locked file, etc
  echo "LOCKED AT $locktime by $BASELOGPATH/$RUN_TYPE.lock.txt"
  mailout "locked"
  exit
fi

setlocked "$RUN_TYPE" true "$thedate"


RUNLOGPATH="$BASELOGPATH/log/$RUN_TYPE/$RUN_TYPE-$thedate"
RUNTMPPATH="$BASELOGPATH/tmp/$RUN_TYPE"
mkdir -p "$RUNLOGPATH/"

LOGSUFFIX="$RUN_TYPE-$thedate.txt"


rebuildtmpfiles



if [ "$HAS_BLOCKID" == true ]; then
  loadblockids
  loadmounts "cmount.txt"

  touch  "$RUNTMPPATH/mounted.txt"
  touch  "$RUNTMPPATH/unmounted.txt"

  findmounted
  automount

  cat "$RUNTMPPATH/unmounted.txt" > "$RUNTMPPATH/oldunmounted.txt"

  rebuildtmpfiles
  loadblockids

  loadmounts "cmount.txt"

  touch  "$RUNTMPPATH/mounted.txt"
  touch  "$RUNTMPPATH/unmounted.txt"
  findmounted
else
  loadmounts "mounted.txt"
fi

ERROR_FAIL=false
verifydriveflags
findcopypaths

if [ "$VALID_CHECK" == true ]; then
  PRE_ERROR_FAIL=false
  extralist=""

  pyrun=$(python raidcheck.py "$extralist" | tail)
  vlogpath=false
  for n in ${pyrun[@]}; do
    if echo "$n" | grep -qP "^\s*\-\s*logged in\:\s*"; then
      vlogpath=$(echo "$n" | grep -oP "\/.*$")
    fi
  done
  if [ ! "$vlogpath" == false ]; then
    vdate=$(echo "$vlogpath" | grep -oP "(?<=master\-)\d+\-\d+(?=\.txt\s*$)")
    vpath=$(echo "$vlogpath" | grep -oP "^\/.*\/(?=master-[^\/]+\/[^\/]+\.txt\s*$)")
    vsummary="$vpath""md5vali-summary-$vdate.txt"
    for m in $(cat "$vsummary"); do
      echo "z $m"
      if echo "$m" | grep -qP "conflicts?\s*\:\s*\d+"; then
        PRE_ERROR_FAIL=true
        ERROR_FAIL=true
        touch "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
        echo -e "ERROR: CONFLICT FOUND IN VALIDATOR RUN:  '$vsummary'\n" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
        echo -e "--------------------------\n" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
        break
      fi
    done
  fi
  if [ "$PRE_ERROR_FAIL" == true ]; then
    thedate2="$(date +'%Y%m%d_T%H%M')"
    mailout "pre_error"
    exit 0
  fi
fi


prefregstr="(?:\d+\/\d+\/\d+\s+\d+\:\d+\:\d+\s+\[\d+\]\s+)?"
if [ "$PRE_CHECK" == true ]; then
  PRE_ERROR_FAIL=false
  for j in $(cat "$RUNTMPPATH/copypaths.txt"); do
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

    echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX.tmp"
    if [ -e "$drivepath/$sourcepath" ] && [ -e "$targetdrivepath/$targetpath" ]; then
      if [ -d "$drivepath/$sourcepath" ]; then
        rsync -hrltzWPSD --no-links --dry-run --delete --delete-after --no-compress --log-file="$RUNTMPPATH/rsynclog.txt" "$drivepath/$sourcepath" "$targetdrivepath/$targetpath"
      elif [ -f "$drivepath/$sourcepath" ]; then
        rsync -hrltzWPSD --no-links --dry-run --no-compress --log-file="$RUNTMPPATH/rsynclog.txt" "$drivepath/$sourcepath" "$targetdrivepath/$targetpath"
      fi
    elif [ ! -e "$drivepath/$sourcepath" ]; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo -e "ERROR: PATH '$drivepath/$sourcepath' NOT FOUND for source drive '$sourceflag'\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
      echo -e "--------------------------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
    elif [ ! -e "$targetdrivepath/$targetpath" ]; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      echo -e "ERROR: PATH '$targetdrivepath/$targetpath' NOT FOUND for target drive '$targetflag'\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
      echo -e "--------------------------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
    fi

    if [ ! "$?" == "0" ]; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      errlabel=$(getrsyncerrcode "$?")
      echo -e "------ $? : $errlabel ------\n" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX.tmp"
    fi

    if grep -qP "^$prefregstr\s*rsync\:.*\: Permission denied \(\d+\)\s*$" "$RUNTMPPATH/rsynclog.txt"; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      grep -nP "^$prefregstr\s*rsync\:.*\: Permission denied \(\d+\)\s*$" "$RUNTMPPATH/rsynclog.txt" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX.tmp"
    fi
    if grep -qP "^$prefregstr\s*rsync\:.*\: Operation not permitted \(\d+\)\s*$" "$RUNTMPPATH/rsynclog.txt"; then
      LOOP_ERROR_FAIL=true
      PRE_ERROR_FAIL=true
      ERROR_FAIL=true
      grep -nP "^$prefregstr\s*rsync\:.*\: Operation not permitted \(\d+\)\s*$" "$RUNTMPPATH/rsynclog.txt" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX.tmp"
    fi

    rm -f "$RUNTMPPATH/rsynclog.txt"

    if [ "$LOOP_ERROR_FAIL" == true ]; then
      cat "$RUNLOGPATH/prelog_errs-$LOGSUFFIX.tmp" >> "$RUNLOGPATH/prelog_errs-$LOGSUFFIX"
    fi
    rm -f "$RUNLOGPATH/prelog_errs-$LOGSUFFIX.tmp"
  done
  if [ "$PRE_ERROR_FAIL" == true ]; then
    thedate2="$(date +'%Y%m%d_T%H%M')"
    mailout "pre_error"
    exit 0
  fi
fi

if [ "$ERROR_FAIL" == true ]; then
  thedate2="$(date +'%Y%m%d_T%H%M')"
  mailout "error"
  exit 0
fi
if [ "$PREP_ONLY" == true ]; then
  exit 0
fi

ERROR_FAIL=false
df -h >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"

for j in $(cat "$RUNTMPPATH/copypaths.txt"); do
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

  tmpfile="$RUNLOGPATH/log_full-$LOGSUFFIX.tmp"
  rm -f "$tmpfile"


  echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
  if [ -e "$drivepath/$sourcepath" ] && [ -e "$targetdrivepath/$targetpath" ]; then
    if [ -d "$drivepath/$sourcepath" ]; then
      echo "a $j"
      rsync -hrltvvzWPSD --no-links --delete --delete-after --stats --no-compress --log-file="$tmpfile" "$drivepath/$sourcepath" "$targetdrivepath/$targetpath"
    elif [ -f "$drivepath/$sourcepath" ]; then
      echo "b $j"
      rsync -hrltvvzWPSD --no-links --stats --no-compress --log-file="$tmpfile" "$drivepath/$sourcepath" "$targetdrivepath/$targetpath"
    fi
  elif [ ! -e "$drivepath/$sourcepath" ]; then
    ERROR_FAIL=true
    LOOP_ERROR_FAIL=true
    echo -e "ERROR: PATH '$drivepath/$sourcepath' NOT FOUND for source drive '$sourceflag'\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
    echo -e "--------------------------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
  elif [ ! -e "$targetdrivepath/$targetpath" ]; then
    ERROR_FAIL=true
    LOOP_ERROR_FAIL=true
    echo -e "ERROR: PATH '$targetdrivepath/$targetpath' NOT FOUND for target drive '$targetflag'\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
    echo -e "--------------------------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
  fi

  if [ ! "$?" == "0" ]; then
    ERROR_FAIL=true
    LOOP_ERROR_FAIL=true
    errlabel=$(getrsyncerrcode "$?")
    echo -e "------ $? : $errlabel ------\n" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
  fi
  if grep -qP "^$prefregstr\s*rsync\:.*\: Permission denied \(\d+\)\s*$" "$tmpfile"; then
    ERROR_FAIL=true
    LOOP_ERROR_FAIL=true
    grep -nP "^$prefregstr\s*rsync\:.*\: Permission denied \(\d+\)\s*$" "$tmpfile" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
  fi
  if grep -qP "^$prefregstr\s*rsync\:.*\: Operation not permitted \(\d+\)\s*$" "$tmpfile"; then
    ERROR_FAIL=true
    LOOP_ERROR_FAIL=true
    grep -nP "^$prefregstr\s*rsync\:.*\: Operation not permitted \(\d+\)\s*$" "$tmpfile" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"
  fi


  echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_deletes-$LOGSUFFIX"
  echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_copies-$LOGSUFFIX"
  echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_folders-$LOGSUFFIX"
  echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_matches-$LOGSUFFIX"
  grep -P "^$prefregstr\s*deleting\s+.*" "$tmpfile" >> "$RUNLOGPATH/log_deletes-$LOGSUFFIX"
  grep -P "^$prefregstr\s*>f\+{9,10}\s+\S.*[^\s\/]\s*$" "$tmpfile" >> "$RUNLOGPATH/log_copies-$LOGSUFFIX"
  grep -P "^$prefregstr\s*cd\+{9,10}\s+\S.*\/\s*$" "$tmpfile" >> "$RUNLOGPATH/log_folders-$LOGSUFFIX"
  grep -P "^$prefregstr\s*\S.*\s+is uptodate\s*$" "$tmpfile" >> "$RUNLOGPATH/log_matches-$LOGSUFFIX"


  ##################################### improve
  echo -e "\n--------- $sourcepath ----------\n" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
  for g in $(grep -P "^$prefregstr\s*total\:\s+matches=\d+\s+hash_hits=\d+\s+false_alarms=\d+\s+data=\d+\s*$" "$tmpfile"); do
    nv=$(grep -nP "^$prefregstr\s*total\:\s+matches=\d+\s+hash_hits=\d+\s+false_alarms=\d+\s+data=\d+\s*$" "$tmpfile")
    nval=$(echo "$nv" | grep -oP "^\d+(?=\:)")
    nv2=$(grep -nP "^$prefregstr\s*Number of files\:\s*[\d\.\,]+\s*\(reg\:\s*[\d\.\,]+,\s*dir\:\s*[\d\.\,]+\)\s*$" "$tmpfile")
    nval2=$(echo "$nv2" | grep -oP "^\d+(?=\:)")

    tail "-n+$nval" "$tmpfile"| head -n 1 >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
    tail "-n+$nval2" "$tmpfile" >> "$RUNLOGPATH/log_shortened-$LOGSUFFIX"
  done
  #####################################

  if [ "$LOOP_ERROR_FAIL" == true ]; then
    cat "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp" >> "$RUNLOGPATH/log_errs-$LOGSUFFIX"
  fi
  rm -f "$RUNLOGPATH/log_errs-$LOGSUFFIX.tmp"

  #  cat "$RUNLOGPATH/log_full-$LOGSUFFIX.tmp" >> "$RUNLOGPATH/log_full-$LOGSUFFIX"
  rm -f "$RUNLOGPATH/log_full-$LOGSUFFIX.tmp"
done
thedate2="$(date +'%Y%m%d_T%H%M')"
if [ "$ERROR_FAIL" == true ]; then
  mailout "error"
else
  mailout "summary"
fi

#####################################################################

##autounmount

setlocked "$RUN_TYPE" false "$thedate"

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

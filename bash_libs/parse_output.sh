#!/bin/bash
IFS=$'\n'



greprsynclines() {
  ## DEFUNCT FUNCTION
  pref="^\d+\/\d+\/\d+\s+\d+\:\d+\:\d+\s+\[\d+\]\s+"
  nopermission=("^rsync\:.*\: Permission denied \(\d+\)\s*$")
  notpermitted=("^rsync\:.*\: Operation not permitted \(\d+\)\s*$")
  reporting=()
  reporting+=("^(?:sent|total)\s*(?:size is|\: matches=)?\s*\d+")
  reporting+=("rsync error\:.*$")
  drek=()
  ##
}
parsevalidsummary() {
  parsefile="$1"
  targetfile="$2"
  if grep -qP "-------------totals----------" "$parsefile"; then
    for g in $(grep -P "-------------totals----------" "$parsefile"); do
      nv=$(grep -nP "-------------totals----------" "$parsefile")
      nval=$(echo "$nv" | grep -oP "^\d+(?=\:)")

      tail "-n+$nval" "$parsefile" >> "$targetfile"
      break
    done
  fi
}
parsersync() {
  parsefile="$1"
  targetfile="$2"

  if grep -qP "^$prefregstr\s*total\:\s+matches=\d+\s+hash_hits=\d+\s+false_alarms=\d+\s+data=\d+\s*$" "$parsefile"; then
    for g in $(grep -P "^$prefregstr\s*total\:\s+matches=\d+\s+hash_hits=\d+\s+false_alarms=\d+\s+data=\d+\s*$" "$parsefile"); do
      nv=$(grep -nP "^$prefregstr\s*total\:\s+matches=\d+\s+hash_hits=\d+\s+false_alarms=\d+\s+data=\d+\s*$" "$parsefile")
      nval=$(echo "$nv" | grep -oP "^\d+(?=\:)")
      nv2=$(grep -nP "^$prefregstr\s*Number of files\:\s*[\d\.\,]+\s*\(reg\:\s*[\d\.\,]+,\s*dir\:\s*[\d\.\,]+\)\s*$" "$parsefile")
      nval2=$(echo "$nv2" | grep -oP "^\d+(?=\:)")

      if [ -e "$parsefile.2" ]; then
        rm -f "$parsefile.2"
      fi
      tail "-n+$nval" "$parsefile"| head -n 1 >> "$parsefile.2"
      tail "-n+$nval2" "$parsefile" >> "$parsefile.2"

      for h in $(cat "$parsefile.2"); do
        if echo "$h" | grep -qP "^\d+(?:\/\d+)+\s+\d+(?:\:\d+)+\s+\[\d+\]\s+(?:[Tt]otal|Number of|Literal data|Matched data|sent)"; then
          tmpline=$(echo "$h" | sed -e 's/^[[:digit:]]*\/[[:digit:]]*\/[[:digit:]]*[[:space:]][[:digit:]]*\:[[:digit:]]*\:[[:digit:]]*[[:space:]]\[[[:digit:]]*\][[:space:]]//g')
          echo "$tmpline" >> "$targetfile"
        fi
      done
      rm -f "$parsefile.2"
    done
  elif grep -qP "^$prefregstr\s*Number of files\:\s+[\d\.\,]+\s+\(reg\:\s+[\d\.\,]+\,\s+dir\:\s+[\d\.\,]+\)" "$parsefile"; then
    for h in $(cat "$parsefile"); do
      if echo "$h" | grep -qP "^\d+(?:\/\d+)+\s+\d+(?:\:\d+)+\s+\[\d+\]\s+(?:[Tt]otal|Number of|Literal data|Matched data|sent)"; then
        tmpline=$(echo "$h" | sed -e 's/^[[:digit:]]*\/[[:digit:]]*\/[[:digit:]]*[[:space:]][[:digit:]]*\:[[:digit:]]*\:[[:digit:]]*[[:space:]]\[[[:digit:]]*\][[:space:]]//g')
        echo "$tmpline" >> "$targetfile"
      fi
    done
  fi
}

readrsyncline() {
  ## DEFUNCT??
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


grepRSyncFailure() {
  prefregstr="$1"
  thetmpfile="$2"
  logresult="$3"
  if grep -qP "^$prefregstr\s*rsync\:.*\: Permission denied \(\d+\)\s*$" "$thetmpfile"; then
    grep -nP "^$prefregstr\s*rsync\:.*\: Permission denied \(\d+\)\s*$" "$thetmpfile" >> "$logresult"
    echo "fail_1 "
  fi
  if grep -qP "^$prefregstr\s*rsync\:.*\: Operation not permitted \(\d+\)\s*$" "$thetmpfile"; then
    echo "fail_2 "
    grep -nP "^$prefregstr\s*rsync\:.*\: Operation not permitted \(\d+\)\s*$" "$thetmpfile" >> "$logresult"
  fi
}

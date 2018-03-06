#!/bin/bash
IFS=$'\n'

checklocked() {
  ignore_locks=$1
  baselogpath="$2"
  lockedrunname="$3"

  if [ -f "$baselogpath/$lockedrunname.lock.txt" ]; then
    if [ "$ignore_locks" == true ]; then
      rm -f "$baselogpath/$lockedrunname.lock.txt"
      false
    else
      true
    fi
  else
    false
  fi
}
getlocked() {
  baselogpath="$1"
  lockedrunname="$2"
  echo "$baselogpath/$lockedrunname.lock.txt"
}
setlocked() {
  baselogpath="$1"
  lockedrunname="$2"
  setlocked="$3"
  time="$4"
  if [ "$setlocked" == true ]; then
    if [ ! -d "$baselogpath/" ]; then
      mkdir -p "$baselogpath/"
    fi
    if [ ! -f "$baselogpath/$lockedrunname.lock.txt" ]; then
      echo "$time" > "$baselogpath/$lockedrunname.lock.txt"
    fi
  else
    if [ -f "$baselogpath/$lockedrunname.lock.txt" ]; then
      rm -f "$baselogpath/$lockedrunname.lock.txt"
    fi
  fi
}

rebuildtmpfiles() {
  runtmppath="$1"

  if [ ! -d "$runtmppath" ]; then
    mkdir -p "$runtmppath"
  fi
  tmpfiles=("blkid.txt" "unmounted.txt" "cmount.txt" "mounted.txt" "dmount.txt" "copypaths.txt" "rsynclog.txt")
  for p in ${tmpfiles[@]}; do
#   pname="${tmpfiles["$p"]}"
    pname="$p"
    if [ -f "$runtmppath/$pname" ]; then
      rm -f "$runtmppath/$pname"
    fi
  done
}

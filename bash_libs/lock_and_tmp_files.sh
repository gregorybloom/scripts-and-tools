#!/bin/bash
IFS=$'\n'

checklocked() {
  ignore_locks=$1
  baselockpath="$2"
  lockedrunname="$3"

  if [ -f "$baselockpath/$lockedrunname.lock.txt" ]; then
    if [ "$ignore_locks" == true ]; then
      rm -f "$baselockpath/$lockedrunname.lock.txt"
      false
    else
      true
    fi
  else
    false
  fi
}
getlocked() {
  baselockpath="$1"
  lockedrunname="$2"
  echo "$baselockpath/$lockedrunname.lock.txt"
}
setlocked() {
  baselockpath="$1"
  lockedrunname="$2"
  setlocked="$3"
  time="$4"
  if [ "$setlocked" == true ]; then
    if [ ! -d "$baselockpath/" ]; then
      mkdir -p "$baselockpath/"
    fi
    if [ ! -f "$baselockpath/$lockedrunname.lock.txt" ]; then
      echo "$time" > "$baselockpath/$lockedrunname.lock.txt"
    fi
  else
    if [ -f "$baselockpath/$lockedrunname.lock.txt" ]; then
      rm -f "$baselockpath/$lockedrunname.lock.txt"
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

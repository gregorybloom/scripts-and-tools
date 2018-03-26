#!/bin/bash
IFS=$'\n'

search_log_dupes() {

  searchlogpath="$1"
  finallog="$2"
  tmppath="$3"

  mkdir -p "$tmppath"
  tmpfile="$tmppath/test.txt"

  sudo rm -fv "$finallog.tmp";
  touch "$finallog.tmp";

  lastmd5=""

  sortedlog="$tmppath/sorted.txt"
  sort -u "$searchlogpath" > "$sortedlog"
  for line in $(cat "$sortedlog"); do
    md5line=$(echo "$line" | grep -oP "^[\da-f]{16,61}");
    if echo "$md5line" | grep -qP "^[\da-f]{16,61}$"; then
      if [ "$md5line" == "$lastmd5" ]; then
        continue
      else
        lastmd5="$md5line"
        resarr=$(grep -irP "^$md5line" "$sortedlog");
        echo "$resarr" > "$tmpfile";
        if wc -l "$tmpfile" | grep -qP "^1\s+\/"; then
          touch "$tmpfile";
        else
          echo "$resarr" >> "$finallog.tmp";
        fi;
      fi;
    fi;
  done;
  sort -u "$finallog.tmp" > "$finallog";
}

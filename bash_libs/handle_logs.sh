#!/bin/bash
IFS=$'\n'



removeoldlogs() {
  targetfolder="$1"
  nameregex="$2"
  tmppath="$3"
  filecount="$4"

  rm -f "$tmppath/oldlist.txt"
  touch "$tmppath/oldlist.txt"
  for i in $(ls -1 "$targetfolder"); do
    if echo "$i" | grep -qP "$nameregex"; then
        echo "$i" >> "$tmppath/oldlist.txt"
    fi
  done
  total=$(wc -l "$tmppath/oldlist.txt" | grep -oP "^\d+")
  if [ "$total" -lt "$filecount" ]; then
    echo "total logs less than max: $total"
#    return
  fi


  plusone=$((filecount+1))
  sort -ru "$tmppath/oldlist.txt" > "$tmppath/oldlist.sorted.txt"
  tail -n+"$plusone" "$tmppath/oldlist.sorted.txt" > "$tmppath/oldlist.drop.txt"

  echo -e "\n"
  wc -l "$tmppath/oldlist.sorted.txt"
  wc -l "$tmppath/oldlist.drop.txt"
  echo -e "\n"

  for i in $(cat "$tmppath/oldlist.drop.txt"); do
    if echo "$i" | grep -qP "$nameregex"; then
      if [ -f "$targetfolder/$i" ]; then
        echo "removed: $targetfolder/$i"
        rm -f "$targetfolder/$i"
      elif [ -d "$targetfolder/$i" ]; then
        echo "removed: $targetfolder/$i"
        rm -Rf "$targetfolder/$i"
      fi
    fi
  done
}

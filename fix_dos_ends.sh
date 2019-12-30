#!/bin/bash

IFS=$'\n'

sedfile() {
  thefile="$1"
  if [ -e "$thefile.tmp" ]; then
    echo "Error on $thefile.tmp"
    return
  fi
  sed -e "s/\+$//" "$thefile" > "$thefile.tmp"
  rm -f "$thefile"
  mv "$thefile.tmp" "$thefile"
}


if [ -z "$1" ]; then
  echo "No target provided.  Add a folder or file path."
  exit 0
else
  target="$1"
fi

if [ -f "$target" ]; then
  sedfile "$target"
else
  for path in $(find "$target" -type f); do
    sedfile "$path"
  done
fi

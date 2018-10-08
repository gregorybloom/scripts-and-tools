#!/bin/bash
IFS=$'\n'



loadblockids() {
  for a in $(blkid); do
    # Unable to start 'blkid': The specified file was not found.
    SAVEDRIVE=false
    if echo "$a" | grep -qP "^\/dev\/\w+\:\sLABEL=\"[\w\-\s]+\""; then
      SAVEDRIVE=true
    elif echo "$a" | grep -qP "^\/dev\/md\d+"; then
      SAVEDRIVE=true
    fi
    if [ "$SAVEDRIVE" == true ]; then
      uuid=$(echo "$a" | grep -oP "(?<=\sUUID=\")[\w\-]+(?=\")")
      type=$(echo "$a" | grep -oP "(?<=\sTYPE=\")[\w\-]+(?=\")")
      path=$(echo "$a" | grep -oP "^[^\:\s]+(?=\:)")
      label=$(echo "$a" | grep -oP "(?<=\sLABEL=\")[^\"]+(?=\")")
      echo "$uuid,$type,$path,$label" >> "$RUNTMPPATH/blkid.txt"
    fi
  done
}
loadmounts() {
  runtmppath="$1"
  filename="$2"
  for b in $(mount); do
    if echo "$b" | grep -qP "^(?:[A-Z]\:)?[\w\-\/]* on \/[^\s]+ type \w+ \([^\(\)]+\)$"; then
     opath=$(echo "$b" | grep -oP "^(?:(?<=\w\:)|(?<=))[^\s]+(?= on )")
     dpath=$(echo "$b" | grep -oP "(?<= on )\/[^\s]+(?= type)")
     dtype=$(echo "$b" | grep -oP "(?<= type )\w+(?= \([^\(\)]+\)$)")
     echo "$opath,$dpath,$dtype" >> "$runtmppath/$filename"
   fi
 done
}
findmounted() {
  runtmppath="$1"
  for i in $(cat "$runtmppath/blkid.txt"); do
    IFS=',' read -ra vals <<< "$i"    #Convert string to array
    uuid=${vals[0]}
    type=${vals[1]}
    path=${vals[2]}
    label=${vals[3]}
    MOUNT_FOUND=false
    for j in $(cat "$runtmppath/cmount.txt"); do
      IFS=',' read -ra vals2 <<< "$j"    #Convert string to array
      opath=${vals2[0]}
      dpath=${vals2[1]}
      dtype=${vals2[2]}
      if [[ "$opath" == "$path" ]]; then
        echo "$opath,$dpath,$dtype" >> "$runtmppath/mounted.txt"
        MOUNT_FOUND=true
        break
      fi
    done
    if [ "$MOUNT_FOUND" == false ]; then
     echo "$uuid,$type,$path,$label" >> "$runtmppath/unmounted.txt"
   fi
 done
}
autounmount() {
  runtmppath="$1"
  for i in $(cat "$runtmppath/newmounted.txt"); do
      IFS=',' read -ra vals2 <<< "$j"    #Convert string to array
      thetype=${vals2[0]}
      opath=${vals2[1]}
      dpath=${vals2[2]}
      umount -vl "$dpath"
  done
}
automount() {
  runtmppath="$1"
  if [ ! -f "$runtmppath/newmounted.txt" ]; then
    rm -f "$runtmppath/newmounted.txt"
  fi
  touch "$runtmppath/newmounted.txt"

  mountnames=()
  for i in $(ls -l "/media/"); do
    if echo "$i" | grep -qP "d[\w\-\.]+\s*\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\d+\s+(?:\d+\:)?\d+\s+\w+\s*$"; then
      mname=$(echo "$i" | grep -oP "(?<=\s)\w+\s*$")
      mountnames+=($mname)
    fi
  done
  for j in $(cat "$runtmppath/unmounted.txt"); do
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
      touch "$runtmppath/newmounted.txt"

      sudo mount -t "auto" "$path" "/media/$targetname"
      echo "auto,$path,/media/$targetname" >> "$runtmppath/newmounted.txt"
    fi
  done
}
verifydriveflags() {
  runtmppath="$1"
  mv "$runtmppath/mounted.txt" "$runtmppath/mounted.tmp.txt"
  touch "$runtmppath/mounted.txt"
  for j in $(cat "$runtmppath/mounted.tmp.txt"); do
    IFS=',' read -ra vals4 <<< "$j"    #Convert string to array
    opath=${vals4[0]}
    path=${vals4[1]}
    type=${vals4[2]}
    DRIVE_FLAG=false
    for k in $(ls -l "$path"); do
      if echo "$k" | grep -qP "^\-[\w\-\.+]+\s*\d+\s+[\w\+]+\s+[\w\+]+\s+\d+\s+\w+\s+\d+\s+(?:\d+\:)?\d+\s+_DRIVEFLAG_\w+_\.txt\s*$"; then
        DRIVE_FLAG=$(echo "$k" | grep -oP "(?<=\s)_DRIVEFLAG_\w+_(?=\.txt\s*$)")
        break
      fi
    done
    if [ "$DRIVE_FLAG" == false ]; then
      continue
    fi
    echo "$opath,$path,$type,$DRIVE_FLAG"
    echo "$opath,$path,$type,$DRIVE_FLAG" >> "$runtmppath/mounted.txt"
  done
}

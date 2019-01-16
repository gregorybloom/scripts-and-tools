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
    echo "$SAVEDRIVE,$a"
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

function array_contains() {
    local n=$#
    local value=${!n}
    for ((i=1;i < $#;i++)) {
        if [ "${!i}" == "${value}" ]; then
            echo "y"
            return 0
        fi
    }
    echo "n"
    return 1
}

builddrivepaths() {
  runtmppath="$1"
  drivepathfile="$2"
  rm -f "$drivepathfile"
  touch "$drivepathfile"

  foundflags=()
  if [ -d "/drives/" ]; then
      for i in $(ls -1 "/drives/"); do
          for j in $(ls -1 "/drives/$i/"); do
              if echo "$j" | grep -qP "^_DRIVEFLAG_\w+\.txt$"; then
                  flagfile=$(echo "$j" | grep -oP "^_DRIVEFLAG_\w+")
                  if [ $(array_contains "${foundflags[@]}" "$flagfile") == "n" ]; then
                    foundflags+=("$flagfile")
                    echo "/xde/xx,/drives/$i,xx,$flagfile" >> "$drivepathfile"
                  fi
              fi
          done
      done
  fi
  if [ -d "/media/" ]; then
      for i in $(ls -1 "/media/"); do
          for j in $(ls -1 "/media/$i/"); do
              if echo "$j" | grep -qP "^_DRIVEFLAG_\w+\.txt$"; then
                  flagfile=$(echo "$j" | grep -oP "^_DRIVEFLAG_\w+")
                  if [ $(array_contains "${foundflags[@]}" "$flagfile") == "n" ]; then
                    foundflags+=("$flagfile")
                    echo "/xde/xx,/media/$i,xx,$flagfile" >> "$drivepathfile"
                  fi
              fi
          done
      done
  fi
}

verifydriveflags() {
  runtmppath="$1"
  drivepathfile="$2"
  mv "$drivepathfile" "$drivepathfile.tmp"
  touch "$drivepathfile"
  for j in $(cat "$drivepathfile.tmp"); do
    IFS=',' read -ra vals4 <<< "$j"    #Convert string to array
    opath=${vals4[0]}
    path=${vals4[1]}
    type=${vals4[2]}
    DRIVE_FLAG=false
    for k in $(ls -1 "$path"); do
      if echo "$k" | grep -qP "^_DRIVEFLAG_\w+_\.txt\s*$"; then
        DRIVE_FLAG=$(echo "$k" | grep -oP "_DRIVEFLAG_\w+_(?=\.txt\s*$)")
        break
      fi
    done
    if [ "$DRIVE_FLAG" == false ]; then
      continue
    fi
    echo "$opath,$path,$type,$DRIVE_FLAG"
    echo "$opath,$path,$type,$DRIVE_FLAG" >> "$drivepathfile"
  done
}

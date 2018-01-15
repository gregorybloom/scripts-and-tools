#!/bin/bash

timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}

currtime=$(timestamp)
echo "time: $currtime"



source "config/findsshkeypath.sh"
source "config/grab_server100_info.sh"

CONFIGDUMP="$_SERVERBACKDUMP/Config/configdump"
MONGODUMP="$_SERVERBACKDUMP/Mongo/mongodump"
NODEDUMP="$_SERVERBACKDUMP/NodeFiles/filedump"

BACKUPLIST="config/100_backup_list.txt"

RETRIEVEPATH="../../retrieve"
SCRIPTTMP="./tmp"

rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/ret_tmp"
chmod 755 -R "$RETRIEVEPATH"

# #########################################################################################
# Download '_SERVER100_SITESAVAIL' to /retrieve, copy to 'CONFIGDUMP'
rsync --exclude-from 'r_excludes.txt' --temp-dir='ret_tmp' -e "ssh -i $sshkey -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_SITESAVAIL" "$RETRIEVEPATH"
rm -rf "$RETRIEVEPATH/ret_tmp"

mkdir -p "$CONFIGDUMP"

rsync -a "$RETRIEVEPATH/" "$CONFIGDUMP"

# Zip 'CONFIGDUMP', move to 'CONFIGDUMPs' path folder
mv "$CONFIGDUMP" "$SCRIPTTMP/configdump"
tar cvzf "$SCRIPTTMP/configdump.tar.gz" "$SCRIPTTMP/configdump"
mv "$SCRIPTTMP/configdump.tar.gz" "$CONFIGDUMP_$currtime.tar.gz"
rm -rfv "$SCRIPTTMP/configdump"

rm -rf "$RETRIEVEPATH"

# #########################################################################################

visitedarr=()
for a in $(cat "$BACKUPLIST"); do
  IFS=',' read -ra vals1 <<< "$a"    #Convert string to array
  nodeappname=${vals1[0]}
  mongodb=${vals1[1]}

  # have we already checked and scanned this group? go on if so
  grouppath="$nodeappname,$mongodb"
  groupfound=false
  for i in "${visitedarr[@]}"; do
    if [ "$i" == "$grouppath" ] ; then
        groupfound=true
        break
    fi
  done
  if [ "$groupfound" == true ]; then
    continue
  fi
  visitedarr+=("$grouppath")

# go to nodechat, build list of mongo tables
  IFS=$'\n'
  STUFF=$(ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$sshkey" -o PreferredAuthentications=publickey -p $_SERVER100_PORT 'cd '"$_SERVER100_WEBPATH/$nodeappname"'; mongo '"$mongodb"' --eval "printjson(db.getMongo().getDBNames())"')
  dblist=()
  for fn in $(echo $STUFF); do
  	LIP=$(echo "$fn" | grep -ioP '\[\s*".*"\s*\]\s*')
  	if(echo "$LIP" | grep -inorP --quiet "^\[.*\]\s*$"); then
  		LIP2=$(echo "$LIP" | grep -ioP '".*"')
  		IFS=$', '
  		for dn in $(echo $LIP2); do
  			if(echo "$dn" | grep -inorP --quiet '^"nodechat_.*"'); then
  				dblist+=("$dn")
  			fi
  		done
  	fi
  	IFS=$'\n'
  done

  # clear mongo dumps on server, dump all tables, tar.gz tables
  ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$sshkey" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" 'cd '"$_SERVER100_WEBPATH/$nodeappname"'; rm mongodump.tar.gz; rm -Rv dump; rm -Rv mongodump'
  for dbi in ${dblist[@]}; do
  	ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$sshkey" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" 'cd '"$_SERVER100_WEBPATH/$nodeappname"'; mongodump --db "$dbi"'
  done
  ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$sshkey" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" 'cd '"$_SERVER100_WEBPATH/$nodeappname"'; mv dump mongodump; tar cvzf mongodump.tar.gz mongodump; rm -Rv mongodump'

  mkdir -p "$RETRIEVEPATH/ret_tmp"
  chmod 755 -R "$RETRIEVEPATH"

  # download tar.gz'd mongo tables
  rsync --exclude-from 'r_excludes.txt' --temp-dir='ret_tmp' -e "ssh -i $sshkey -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_WEBPATH/$nodeappname/mongodump.tar.gz" "$RETRIEVEPATH"
	rm -rf "$RETRIEVEPATH/ret_tmp"

  mv "$RETRIEVEPATH/mongodump.tar.gz" "$MONGODUMP_$nodeappname_$currtime.tar.gz"
  rm -rf "$RETRIEVEPATH"


  # #########################################################################################
  # download from /nodechat, /data and /branches specifically

  mkdir -p "$RETRIEVEPATH/ret_tmp"
  chmod 755 -R "$RETRIEVEPATH"

  pathsarr=()
  for b in $(cat "$BACKUPLIST"); do
    IFS=',' read -ra vals2 <<< "$b"    #Convert string to array
    nodeappname2=${vals2[0]}
    mongodb2=${vals2[1]}

    nodepaths2=${vals2[2]}
    if [ "$nodeappname" == "$nodeappname2" ]; then
      if [ "$mongodb" == "$mongodb2" ]; then
        pathsarr+=("$nodepaths2")
      fi
    fi
  done
  for _pathitem in ${!pathsarr[@]}; do
    nodepath="${pathsarr["$_pathitem"]}"
    rsync --exclude-from 'r_excludes.txt' --temp-dir='ret_tmp' -e "ssh -i $sshkey -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_WEBPATH/$nodeappname/$nodepath" "$RETRIEVEPATH"
  done

  rm -rf "$RETRIEVEPATH/ret_tmp"


  rm -rf "$SCRIPTTMP"
  mkdir -p "$SCRIPTTMP"

  # zip dumped files and save
  rsync -a "$RETRIEVEPATH/" "$SCRIPTTMP"
  tar cvzf filedump.tar.gz "$SCRIPTTMP"
  mv filedump.tar.gz "$NODEDUMP_$currtime.tar.gz"
  rm -Rv "$SCRIPTTMP"

  rm -rf "$RETRIEVEPATH"
done

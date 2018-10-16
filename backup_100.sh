#!/bin/bash

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`


timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}

currtime=$(timestamp)
echo "time: $currtime"


source "config/findsshkeypath.sh"
source "config/grab_server100_info.sh"
source "bash_libs/handle_mounts.sh"


tuser=$(whoami)
lastdir=$(echo "$SCRIPTDIR" | grep -oP "^.*\S")
if echo "$lastdir" | grep -qP "^\/home\/mobaxterm\/"; then
  flast=$(echo "$lastdir" | grep -oP "(?<=^\/home\/mobaxterm\/).*\S")
  cd "/drives/c/Users/$tuser/$flast"
  HOME="/drives/c/Users/$tuser"
fi

echo "found home: $HOME"

RUNTMPPATH="/tmp/autobackup/qtmp"
mkdir -p "$RUNTMPPATH"
rm -f "$RUNTMPPATH/mounted.txt"

#echo "loading mounts"
#loadmounts "$RUNTMPPATH" "mounted.txt"
#echo "verifying flags"
#verifydriveflags "$RUNTMPPATH"
#echo "loaded mounts and located flags"

_SERVERBACKDUMP="${HOME}""$_SERVER100_BACKBASE"

echo "saving to: $_SERVERBACKDUMP"

mkdir -p "$_SERVERBACKDUMP/Config"
mkdir -p "$_SERVERBACKDUMP/Mongo"
mkdir -p "$_SERVERBACKDUMP/NodeFiles"

CONFIGDUMP="$_SERVERBACKDUMP/Config/configdump"
MONGODUMP="$_SERVERBACKDUMP/Mongo/mongodump"
NODEDUMP="$_SERVERBACKDUMP/NodeFiles/filedump"



RETRIEVEPATH="/tmp/retrieve"
SCRIPTTMP="/tmp/scripttmp"


rm -rf "$SCRIPTTMP"
rm -rf "$CONFIGDUMP"
mkdir -p "$SCRIPTTMP/"
mkdir -p "$CONFIGDUMP/"

# #########################################################################################
echo "Downloading server config"
# Download '_SERVER100_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/etc"
chmod 755 -R "$RETRIEVEPATH"
rsync --exclude-from 'config/r_excludes.txt' -e "ssh -i $_SSHKEYPATH -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --safe-links --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_ETCCONF" "$RETRIEVEPATH/etc"

cp -r "$RETRIEVEPATH/etc" "$CONFIGDUMP"

# Download '_SERVER100_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/home"
chmod 755 -R "$RETRIEVEPATH"
rsync --exclude-from 'config/r_excludes.txt' -e "ssh -i $_SSHKEYPATH -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --safe-links --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_HOMEFOLDER" "$RETRIEVEPATH/home" --exclude "*/*/" --include "*"

cp -r "$RETRIEVEPATH/home" "$CONFIGDUMP"

# Zip 'CONFIGDUMP', move to 'CONFIGDUMPs' path folder
mv "$CONFIGDUMP" "$SCRIPTTMP/"
tar cvzf "$SCRIPTTMP/configdump.tar.gz" -C "$SCRIPTTMP" "configdump"
mv "$SCRIPTTMP/configdump.tar.gz" "$CONFIGDUMP""_$currtime.tar.gz"
rm -rfv "$SCRIPTTMP/configdump"

echo "Saved to: ""$CONFIGDUMP""_$currtime.tar.gz"
rm -rf "$RETRIEVEPATH"
# #########################################################################################
source "config/grab_server100_mongo_info.sh"
echo "Downloading mongo dumps"

# go to nodechat, build list of mongo tables
IFS=$'\n'
STUFF=$(ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$_SSHKEYPATH" -o PreferredAuthentications=publickey -p $_SERVER100_PORT 'mongo '"$_SERVER100_ADMINDB" --port $_SERVER100_MONGO_PORT' --eval "printjson(db.getMongo().getDBNames())"')
dblist=()
for fn in $(echo $STUFF); do
	LIP=$(echo "$fn" | grep -ioP '\[\s*".*"\s*\]\s*')
	if(echo "$LIP" | grep -inorP --quiet "^\[.*\]\s*$"); then
		LIP2=$(echo "$LIP" | grep -ioP '".*"')
		IFS=$', '
		for dn in $(echo $LIP2); do
			if(echo "$dn" | grep -inorP --quiet '^"\w+.*"'); then
				dblist+=("$dn")
			fi
		done
	fi
	IFS=$'\n'
done

# clear mongo dumps on server, dump all tables, tar.gz tables
ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$_SSHKEYPATH" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" 'rm -f mongodump.tar.gz; rm -Rvf dump; rm -Rvf mongodump'
for dbi in ${dblist[@]}; do
  echo " - downloading: $dbi"
	ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$_SSHKEYPATH" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" 'mongodump --db "$dbi" --port "'$_SERVER100_MONGO_PORT'"'
done
ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$_SSHKEYPATH" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" 'mv dump mongodump; tar cvzf mongodump.tar.gz mongodump; rm -Rvf mongodump'

mkdir -p "$RETRIEVEPATH/ret_tmp"
chmod 755 -R "$RETRIEVEPATH"

echo "mongodump tarred"
# download tar.gz'd mongo tables
rsync --exclude-from 'config/r_excludes.txt' --temp-dir='ret_tmp' -e "ssh -i $_SSHKEYPATH -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:mongodump.tar.gz" "$RETRIEVEPATH"
rm -rf "$RETRIEVEPATH/ret_tmp"


mv "$RETRIEVEPATH/mongodump.tar.gz" "$MONGODUMP""_$_SERVER100_APPNAME""_$currtime.tar.gz"
echo "mongodump saved to: ""$MONGODUMP""_$_SERVER100_APPNAME""_$currtime.tar.gz"
rm -rf "$RETRIEVEPATH"


ssh "$_SERVER100_USER@$_SERVER100_IP" -i "$_SSHKEYPATH" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" 'rm -f mongodump.tar.gz; rm -Rvf dump; rm -Rvf mongodump'
echo "Done"


# #########################################################################################
# download from /nodechat, /data and /branches specifically
exit  # no node contents worth dumping yet

mkdir -p "$RETRIEVEPATH/ret_tmp"
chmod 755 -R "$RETRIEVEPATH"

pathsarr=()
#for b in $(cat "$BACKUPLIST"); do
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
  rsync --exclude-from 'config/r_excludes.txt' --temp-dir='ret_tmp' -e "ssh -i $_SSHKEYPATH -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_WEBPATH/$nodeappname/$nodepath" "$RETRIEVEPATH"
done

rm -rf "$RETRIEVEPATH/ret_tmp"


rm -rf "$SCRIPTTMP"
mkdir -p "$SCRIPTTMP"

# zip dumped files and save
rsync -a "$RETRIEVEPATH/" "$SCRIPTTMP"
tar cvzf filedump.tar.gz "$SCRIPTTMP"
mv filedump.tar.gz "$NODEDUMP""_$currtime.tar.gz"
rm -Rv "$SCRIPTTMP"

rm -rf "$RETRIEVEPATH"

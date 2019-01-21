#!/bin/bash

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`


timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}

currtime=$(timestamp)
echo "time: $currtime"
_DIR_="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

source "$_DIR_/config/serverinfo/grab_server102_info.sh"
source "$_DIR_/bash_libs/handle_mounts.sh"


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

_SERVERBACKDUMP="${HOME}""$_SERVER102_BACKBASE"

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
mkdir -p "$SCRIPTTMP/"

# #########################################################################################
echo "Downloading server config"
# Download '_SERVER102_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/etc"
chmod 755 -R "$RETRIEVEPATH"

rsync --exclude-from "$_DIR_/config/r_excludes.txt" --exclude-from "$_DIR_/config/serverinfo/server102_excludes.txt" -e "ssh -o PreferredAuthentications=publickey -p $_SERVER102_PORT" -azcW --safe-links --port="$_SERVER102_PORT" "$_SERVER102_USER@$_SERVER102_IP:$_SERVER102_ETCCONF" "$RETRIEVEPATH/etc"
echo "/etc/ rsync complete"

mkdir -p "$SCRIPTTMP/configdump"
cp -r "$RETRIEVEPATH/etc" "$SCRIPTTMP/configdump"

# Download '_SERVER102_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/home"
chmod 755 -R "$RETRIEVEPATH"
rsync --exclude-from "$_DIR_/config/r_excludes.txt" --exclude-from "$_DIR_/config/serverinfo/server102_excludes.txt" -e "ssh -o PreferredAuthentications=publickey -p $_SERVER102_PORT" -azcW --safe-links --port="$_SERVER102_PORT" "$_SERVER102_USER@$_SERVER102_IP:$_SERVER102_HOMEFOLDER" "$RETRIEVEPATH/home" --exclude "*/*/" --include "*"
echo "~/ rsync complete"

cp -r "$RETRIEVEPATH/home" "$SCRIPTTMP/configdump"

# Zip 'CONFIGDUMP', move to 'CONFIGDUMPs' path folder. tar -C "[path/folder]" creates new startpoint for tar
curdir=$(pwd)
cd "$SCRIPTTMP"
tar czf "$SCRIPTTMP/configdump.tar.gz" "configdump"
cd "$curdir"
mv "$SCRIPTTMP/configdump.tar.gz" "$CONFIGDUMP""_$currtime.tar.gz"
rm -rfv "$SCRIPTTMP/configdump"

echo "Saved to: ""$CONFIGDUMP""_$currtime.tar.gz"
rm -rf "$RETRIEVEPATH"
# #########################################################################################
source "$_DIR_/config/serverinfo/grab_server102_mongo_info.sh"
echo "Downloading mongo dumps"

# go to nodechat, build list of mongo tables
IFS=$'\n'
STUFF=$(ssh "$_SERVER102_USER@$_SERVER102_IP" -o PreferredAuthentications=publickey -p $_SERVER102_PORT "mongo '$_SERVER102_ADMINDB' --port $_SERVER102_MONGO_PORT --username '$_SERVER102_ADMINUSER' --password '$_SERVER102_ADMINPASS' --eval 'printjson(db.getMongo().getDBNames())'")
dblist=()
for fn in $(echo $STUFF); do
	LIP=$(echo "$fn" | grep -ioP '\[\s*".*"\s*\]\s*')
	if(echo "$LIP" | grep -inorP --quiet "^\[.*\]\s*$"); then
		LIP2=$(echo "$LIP" | grep -ioP '".*"')
		IFS=$', '
		for dn in $(echo $LIP2); do
			if(echo "$dn" | grep -inorP --quiet '^"\w+.*"'); then
        dnval=$(echo "$dn" | grep -oP '(?<=")(\w+.*)(?=")')
        if [ ! "$dnval" == "config" ] && [ ! "$dnval" == "local" ]; then
			      dblist+=("$dn")
        fi
			fi
		done
	fi
	IFS=$'\n'
done

# clear mongo dumps on server, dump all tables, tar.gz tables
ssh "$_SERVER102_USER@$_SERVER102_IP" -o PreferredAuthentications=publickey -p "$_SERVER102_PORT" 'rm -f mongodump.tar.gz; rm -Rvf dump; rm -Rf mongodump'
for dbi in ${dblist[@]}; do
  echo " - Downloading: $dbi"
	ssh "$_SERVER102_USER@$_SERVER102_IP" -o PreferredAuthentications=publickey -p "$_SERVER102_PORT" "mongodump --db '$dbi' --port '$_SERVER102_MONGO_PORT' --username '$_SERVER102_ADMINUSER' --password '$_SERVER102_ADMINPASS'"
done
ssh "$_SERVER102_USER@$_SERVER102_IP" -o PreferredAuthentications=publickey -p "$_SERVER102_PORT" 'if [ -e dump ]; then mv dump mongodump; tar czf mongodump.tar.gz mongodump; fi; rm -Rf mongodump'

mkdir -p "$RETRIEVEPATH/ret_tmp"
chmod 755 -R "$RETRIEVEPATH"

echo "mongodump tarred"
# download tar.gz'd mongo tables
rsync --exclude-from "$_DIR_/config/r_excludes.txt" --temp-dir='ret_tmp' -e "ssh -o PreferredAuthentications=publickey -p $_SERVER102_PORT" -azcW --port="$_SERVER102_PORT" "$_SERVER102_USER@$_SERVER102_IP:mongodump.tar.gz" "$RETRIEVEPATH"
rm -rf "$RETRIEVEPATH/ret_tmp"

if [ -e "$RETRIEVEPATH/mongodump.tar.gz" ]; then
  mv "$RETRIEVEPATH/mongodump.tar.gz" "$MONGODUMP""_$_SERVER102_APPNAME""_$currtime.tar.gz"
  echo "mongodump saved to: ""$MONGODUMP""_$_SERVER102_APPNAME""_$currtime.tar.gz"
else
  echo "No mongo dump found!!"
fi
rm -rf "$RETRIEVEPATH"


ssh "$_SERVER102_USER@$_SERVER102_IP" -o PreferredAuthentications=publickey -p "$_SERVER102_PORT" 'rm -f mongodump.tar.gz; rm -Rf dump; rm -Rf mongodump'
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
  rsync --exclude-from "$_DIR_/config/r_excludes.txt" --temp-dir='ret_tmp' -e "ssh -i $_SSHKEYPATH -o PreferredAuthentications=publickey -p $_SERVER102_PORT" -azcW --port="$_SERVER102_PORT" "$_SERVER102_USER@$_SERVER102_IP:$_SERVER102_WEBPATH/$nodeappname/$nodepath" "$RETRIEVEPATH"
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

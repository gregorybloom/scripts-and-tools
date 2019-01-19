#!/bin/bash

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`


timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}

currtime=$(timestamp)
echo "time: $currtime"
_DIR_="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

#source "config/findsshkeypath.sh"
source "$_DIR_/config/serverinfo/grab_server111_info.sh"
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

_SERVERBACKDUMP="${HOME}""$_SERVER111_BACKBASE"

echo "saving to: $_SERVERBACKDUMP"

mkdir -p "$_SERVERBACKDUMP/Config"
#mkdir -p "$_SERVERBACKDUMP/Mongo"
#mkdir -p "$_SERVERBACKDUMP/NodeFiles"

CONFIGDUMP="$_SERVERBACKDUMP/Config/configdump"
#MONGODUMP="$_SERVERBACKDUMP/Mongo/mongodump"
#NODEDUMP="$_SERVERBACKDUMP/NodeFiles/filedump"


RETRIEVEPATH="/tmp/retrieve"
SCRIPTTMP="/tmp/scripttmp"


rm -rf "$SCRIPTTMP"
mkdir -p "$SCRIPTTMP/"

# #########################################################################################
echo -e "\nDownloading server config"
# Download '_SERVER111_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/etc"
chmod 755 -R "$RETRIEVEPATH"
echo '------'
#rsync --exclude-from "$_DIR_/config/r_excludes.txt" -e "ssh -o PreferredAuthentications=keyboard-interactive,password -o PubkeyAuthentication=no -p $_SERVER111_PORT" -avvzcWP --safe-links --port="$_SERVER111_PORT" "$_SERVER111_USER@$_SERVER111_IP:$_SERVER111_ETCCONF" "$RETRIEVEPATH/etc"
rsync --exclude-from "$_DIR_/config/r_excludes.txt" --exclude-from "$_DIR_/config/serverinfo/server111_excludes.txt" -e "ssh -o PreferredAuthentications=publickey -p $_SERVER111_PORT" -azcW --safe-links --port="$_SERVER111_PORT" "$_SERVER111_USER@$_SERVER111_IP:$_SERVER111_ETCCONF" "$RETRIEVEPATH/etc"
echo "/etc/ rsync complete"

mkdir -p "$SCRIPTTMP/configdump"
cp -r "$RETRIEVEPATH/etc" "$SCRIPTTMP/configdump"

# Download '_SERVER111_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/home"
chmod 755 -R "$RETRIEVEPATH"
#rsync --exclude-from "$_DIR_/config/r_excludes.txt" -e "ssh -o PreferredAuthentications=keyboard-interactive,password -o PubkeyAuthentication=no -p $_SERVER111_PORT" -avvzcWP --safe-links --port="$_SERVER111_PORT" "$_SERVER111_USER@$_SERVER111_IP:$_SERVER111_HOMEFOLDER" "$RETRIEVEPATH/home" --exclude "*/*/" --include "*" --include "*/*"
rsync --exclude-from "$_DIR_/config/r_excludes.txt" --exclude-from "$_DIR_/config/serverinfo/server111_excludes.txt" -e "ssh -o PreferredAuthentications=publickey -p $_SERVER111_PORT" -azcW --safe-links --port="$_SERVER111_PORT" "$_SERVER111_USER@$_SERVER111_IP:$_SERVER111_HOMEFOLDER" "$RETRIEVEPATH/home" --exclude "*/*/" --include "*" --include "*/*"
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
# download from /nodechat, /data and /branches specifically
exit  # no node contents worth dumping yet

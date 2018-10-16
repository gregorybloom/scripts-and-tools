#!/bin/bash

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`


timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}

currtime=$(timestamp)
echo "time: $currtime"


#source "config/findsshkeypath.sh"
source "config/grab_server111_info.sh"
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
rm -rf "$CONFIGDUMP"
mkdir -p "$SCRIPTTMP/"
mkdir -p "$CONFIGDUMP/"

#echo -e "\nEnter Server111 Password:\n"
#read -s _SERVER111_PASSWORD

# #########################################################################################
echo -e "\nDownloading server config"
# Download '_SERVER111_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/etc"
chmod 755 -R "$RETRIEVEPATH"
rsync --exclude-from 'config/r_excludes.txt' -e "ssh -o PreferredAuthentications=keyboard-interactive,password -o PubkeyAuthentication=no -p $_SERVER111_PORT" -avvzcWP --safe-links --port="$_SERVER111_PORT" "$_SERVER111_USER@$_SERVER111_IP:$_SERVER111_ETCCONF" "$RETRIEVEPATH/etc"

cp -r "$RETRIEVEPATH/etc" "$CONFIGDUMP"

# Download '_SERVER111_ etc config' to /retrieve, copy to 'CONFIGDUMP'
rm -rf "$RETRIEVEPATH"
mkdir -p "$RETRIEVEPATH/home"
chmod 755 -R "$RETRIEVEPATH"
rsync --exclude-from 'config/r_excludes.txt' -e "ssh -o PreferredAuthentications=keyboard-interactive,password -o PubkeyAuthentication=no -p $_SERVER111_PORT" -avvzcWP --safe-links --port="$_SERVER111_PORT" "$_SERVER111_USER@$_SERVER111_IP:$_SERVER111_HOMEFOLDER" "$RETRIEVEPATH/home" --exclude "*/*/" --include "*" --include "*/*"


cp -r "$RETRIEVEPATH/home" "$CONFIGDUMP"

# Zip 'CONFIGDUMP', move to 'CONFIGDUMPs' path folder
mv "$CONFIGDUMP" "$SCRIPTTMP/"
tar cvzf "$SCRIPTTMP/configdump.tar.gz" -C "$SCRIPTTMP" "configdump"
mv "$SCRIPTTMP/configdump.tar.gz" "$CONFIGDUMP""_$currtime.tar.gz"
rm -rfv "$SCRIPTTMP/configdump"

echo "Saved to: ""$CONFIGDUMP""_$currtime.tar.gz"
rm -rf "$RETRIEVEPATH"
# #########################################################################################
# download from /nodechat, /data and /branches specifically
exit  # no node contents worth dumping yet

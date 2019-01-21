#!/bin/bash

basefolder="../"
if pwd | grep -qP "\/scripts\-and\-tools\s*$"; then
	basefolder="../../"
fi
deployfolder="$basefolder/deploy"



TEMP=`getopt -o nzPS: --long existing,exclude:,exclude-from:,include:,include-from: \
     -n 'example.bash' -- "$@"`

if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

#	GET THIS WORKING SOMEHOW??
switches="-a"
servernum="100"
while true ; do
    case "$1" in
				-S) servernum="$2" ; shift  2;;

        -n) switches="$switches -n" ; shift ;;
        -z) switches="$switches -z" ; shift ;;
        -P) switches="$switches -P" ; shift ;;
		--existing) switches="$switches --existing" ; shift ;;
		--exclude) switches="$switches --exclude=\"\`$2'\"" ; shift 2 ;;
		--exclude-from) switches="$switches --exclude-from=\"\`$2'\"" ; shift 2 ;;
		--include) switches="$switches --include=\"\`$2'\"" ; shift 2 ;;
		--include-from) switches="$switches --include-from\"=\`$2'\"" ; shift 2 ;;
        --) shift ; break ;;
        *) echo "Internal error!" ; exit 1 ;;
	esac
done



if [ -z "$1" ]; then
	echo "No deploy folder given."
	exit 0
else
	path="$1"
fi
if echo "$path" | grep -qP "\/scripts\-and\-tools(?:\/|\s*(?!.))"; then
		echo "Will not deploy 'scripts-and-tools'."
		exit 0
elif echo "$path" | grep -qP "^\/\.\.\/deploy(?:\/|\s*(?!.))"; then
		echo "Will not deploy the 'deploy' folder."
		exit 0
elif echo "$path" | grep -qP "^\/\.\.\/retrieve(?:\/|\s*(?!.))"; then
		echo "Will not deploy the 'retrieve' folder."
		exit 0
fi

source "config/serverinfo/grab_server100_info.sh"
source "config/serverinfo/grab_server102_info.sh"


isfolder=1
folderpath="$path"
if [ -d "$path" ]; then
	if echo "$path" | grep -oP "[^/]$"; then
		path="$path/"
	fi
elif [ -f "$path" ]; then
#	filepath=$(echo "$path")
	folderpath=$(echo "$path" | grep -oP "^.*/")
	isfolder=0
fi
if echo "$folderpath" | grep -qP "^\.\.\/.*$"; then
#	folderpath=$(echo "$folderpath" | grep -oP "(?<=^\.\.\/).*$")
	folderpath=$(echo "$folderpath" | sed -e 's/^\(\.\.\/\)*//g')
fi



rm -rf "$deployfolder"
mkdir -p "$deployfolder"
rsync -a --no-links --exclude-from 'config/d_excludes.txt' "$path" "$deployfolder"
chmod 755 -R "$deployfolder"

if [[ "$path" = "./" ]]; then
	path=""
elif echo "$path" | grep -qP "^\.\/.*$"; then
	path=$(echo "$path" | grep -oP "(?<=^\.\/).*$")
fi

servernum="102"
_SERVER_TARGET_USER="$user"
_SERVER_TARGET_IP="127.0.0.1"
_SERVER_TARGET_PORT="22"
_SERVER_TARGET_WEBPATH="/var/www/html"
if [ "$servernum" == "100" ]; then
	_SERVER_TARGET_USER="$_SERVER100_USER"
	_SERVER_TARGET_IP="$_SERVER100_IP"
	_SERVER_TARGET_PORT="$_SERVER100_PORT"
	_SERVER_TARGET_WEBPATH="$_SERVER100_WEBPATH"
elif [ "$servernum" == "102" ]; then
	_SERVER_TARGET_USER="$_SERVER102_USER"
	_SERVER_TARGET_IP="$_SERVER102_IP"
	_SERVER_TARGET_PORT="$_SERVER102_PORT"
	_SERVER_TARGET_WEBPATH="$_SERVER102_WEBPATH"
fi


if [[ "$isfolder" -eq 1 ]]; then
	rsync --no-links --exclude-from 'config/d_excludes.txt' -e "ssh -p $_SERVER_TARGET_PORT -i $_SSHKEYPATH -o PreferredAuthentications=publickey" -avvzcWP --delete --delete-after --port="$_SERVER_TARGET_PORT" "$deployfolder/" "$_SERVER_TARGET_USER@$_SERVER_TARGET_IP:$_SERVER_TARGET_WEBPATH/$folderpath"
else
	rsync --no-links --exclude-from 'config/d_excludes.txt' -e "ssh -p $_SERVER_TARGET_PORT -i $_SSHKEYPATH -o PreferredAuthentications=publickey" -avvzcWP --port="$_SERVER_TARGET_PORT" "$deployfolder/" "$_SERVER_TARGET_USER@$_SERVER_TARGET_IP:$_SERVER_TARGET_WEBPATH/$folderpath"
fi



rm -rf "$deployfolder"

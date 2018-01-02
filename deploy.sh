#!/bin/bash

basefolder="./"
if pwd | grep -qP "\/scripts\-and\-tools\s*$"; then
	basefolder="../"
fi
deployfolder="$basefolder/deploy"





if [ -z "$1" ]; then
	path="$basefolder"
else
	path="$basefolder$1"
fi


source "config/findsshkeypath.sh"
source "config/grab_server100_info.sh"


TEMP=`getopt -o nzP --long existing,exclude:,exclude-from:,include:,include-from: \
     -n 'example.bash' -- "$@"`

if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

#	GET THIS WORKING SOMEHOW??
switches="-a"
while true ; do
    case "$1" in
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




if [ -d "$deployfolder" ]; then
	rm -rf "$deployfolder"
fi
mkdir "$deployfolder"
rsync -a --no-links --exclude-from 'd_excludes.txt' "$path" "$deployfolder"
chmod 755 -R "$deployfolder"

if [[ "$path" = "./" ]]; then
	path=""
elif echo "$path" | grep -qP "^\.\/.*$"; then
	path=$(echo "$path" | grep -oP "(?<=^\.\/).*$")
fi



if [[ "$isfolder" -eq 1 ]]; then
	rsync --no-links --exclude-from 'd_excludes.txt' -e "ssh -p $_SERVER100_PORT -i $_SSHKEYPATH -o PreferredAuthentications=publickey" -avvzcWP --delete --delete-after --port="$_SERVER100_PORT" "$deployfolder/" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_WEBPATH/$folderpath"
else
	rsync --no-links --exclude-from 'd_excludes.txt' -e "ssh -p $_SERVER100_PORT -i $_SSHKEYPATH -o PreferredAuthentications=publickey" -avvzcWP --port="$_SERVER100_PORT" "$deployfolder/" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_WEBPATH/$folderpath"
fi



rm -rf "$deployfolder"

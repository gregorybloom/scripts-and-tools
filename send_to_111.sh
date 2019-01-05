#!/bin/bash

DEPLOYPATH="../../deploy"

if [ -z "$1" ]; then
	path="./"
else
	path="$1"
fi

source "config/serverinfo/grab_server111_info.sh"


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

rm -rf "$DEPLOYPATH"


folderpath="$path"
if [ -d "$path" ]; then
	if echo "$path" | grep -oP "[^/]$"; then
		path="$path/"
	fi
elif [ -f "$path" ]; then
	folderpath=$(echo "$path" | grep -oP "^.*/")
	echo "$folderpath"
fi



mkdir -p "$DEPLOYPATH"
rsync -a --no-links --exclude-from 'd_excludes.txt' "$path" "$DEPLOYPATH"
chmod 755 -R "$DEPLOYPATH"

if [[ "$path" = "./" ]]; then
	path=""
fi




rsync --no-links --exclude-from 'd_excludes.txt' -e "ssh -p $_SERVER111_PORT" -avvzcWP --port="$_SERVER111_PORT" "$DEPLOYPATH/" "$_SERVER111_USER@$_SERVER111_IP:/home/$_SERVER111_USER/scripts/$folderpath"

rm -rf "$DEPLOYPATH"

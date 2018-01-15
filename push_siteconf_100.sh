#!/bin/bash




#if [ -z "$1" ]; then
#	path="./"
#else
#	path="$1"
#fi

source "config/findsshkeypath.sh"
source "config/grab_server100_info.sh"
source "config/grab_server100_pythondata.sh"

DEPLOYPATH="../../deploy"



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


path="$_SERVERBACKDUMP/Config/configdump/sites-available/"

rm -rf "$DEPLOYPATH"
mkdir -p "$DEPLOYPATH"

rsync -a --no-links "$path" "$DEPLOYPATH"
chmod 755 -R "$DEPLOYPATH"

if [[ "$path" = "./" ]]; then
	path=""
fi

rsync --no-links -e "ssh -p $_SERVER100_PORT -i $sshkey -o PreferredAuthentications=publickey" -avvzcWP --delete --delete-after --port="$_SERVER100_PORT" deploy "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_WEBPATH/sites-available/"

echo "Log onto the server to move it to $_SERVER100_SITESAVAIL"

rm -rf "$DEPLOYPATH"

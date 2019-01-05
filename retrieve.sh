#!/bin/bash

source "config/findsshkeypath.sh"
source "config/serverinfo/grab_server100_info.sh"

if [ -d "retrieve" ]; then
	rm -rf ./retrieve
fi


rsync --exclude-from 'config/r_excludes.txt' --temp-dir='retrieve' -e "ssh -i $_SSHKEYPATH -o PreferredAuthentications=publickey -p $_SERVER100_PORT" --delete --delete-after -avvzcWP --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$_SERVER100_WEBPATH/" .

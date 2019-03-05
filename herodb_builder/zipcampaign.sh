#!/bin/bash
export PATH=$PATH:/sbin

IFS=$'\n'


SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`


source "$SCRIPTDIR/config/heroconfdata.sh"


fullpath="$_HEROBACKUPPATH";
droppath="$_DROPBOXPATH";



OPTS=`getopt -o vh: --long verbose,help,campaignid: -n 'parse-options' -- "$@"`
loadopts() {
    echo "$OPTS"
    eval set -- "$OPTS"

    VERBOSE=false
    HELP=false
    READINPUT=true

    while true; do
       case "$1" in
          -v | --verbose ) VERBOSE=true; shift ;;
          -h | --help )    HELP=true; shift ;;
          --campaignid )   CAMPAIGNID="$2"; READINPUT=false; shift 2 ;;
          -- ) shift; break ;;
          * ) break ;;
        esac
    done

}



loadopts


beginzip=false
campaignidlist=false
if [ "$READINPUT" == true ]; then
    echo "Find Campaign Name from:";
    read textname;

    c=0;
    for i in $(grep -P "$textname" "$fullpath/infodump/campaignlist.txt"); do
        echo "[$c] $i";
        c=$((c+1));
    done;

    c=0;
    echo "Select Campaign:";
    read number; target="";
    for i in $(grep -P "$textname" "$fullpath/infodump/campaignlist.txt"); do
        if [ "$c" == "$number" ]; then
            target="$i";
        fi;
        c=$((c+1));
    done;
    if echo "$target" | grep -qP "^\d+, "; then
        campaignid=$(echo "$target" | grep -oP "^\d+");
        campaignidlist=($campaignid)
        beginzip=true
    fi
else
    if echo "$CAMPAIGNID" | grep -qP "^\d+\s*(?:,\s*\d+)*$"; then
        campaignidlist=(${CAMPAIGNID//,/
})
        beginzip=true
    else
        echo "ID error!"
        echo "$CAMPAIGNID"
        exit 1
    fi
fi

echo '-------'
if [ "$beginzip" == true ]; then
    for back in ${campaignidlist[@]}; do
        campaignid="$back"
        echo "$campaignid"
        if [ -d "$fullpath/campaigns/$campaignid" ]; then
            for i in $(grep -P "^$campaignid," "$fullpath/infodump/campaignlist.txt"); do
                campaignname=$(echo "$i" | grep -oP "(?<=\d,\s).*")
                echo "$campaignid, $campaignname"

                newname="${campaignname//[^A-Za-z0-9_]/_}";
                curpath=$(pwd)
                cd "$fullpath"
                zip -r "$fullpath/$newname-$campaignid.zip" "campaigns/$campaignid" > /dev/null;
                cd "$curpath"
                echo "";
                ls -l "$fullpath/$newname-$campaignid.zip";

                for j in $(ls -1 /drives/); do
                    echo "/drives/$j/$droppath"
                    if [ -d "/drives/$j/$droppath" ] && [ -f "$fullpath/$newname-$campaignid.zip" ]; then
                        echo "$fullpath/$newname-$campaignid.zip"
                        if [ -f "/drives/$j/$droppath/$newname-$campaignid.zip" ]; then
                            rm -f "/drives/$j/$droppath/$newname-$campaignid.zip";
                        fi;
                        mv "$fullpath/$newname-$campaignid.zip" "/drives/$j/$droppath/$newname-$campaignid.zip";
                        ls -l "/drives/$j/$droppath/$newname-$campaignid.zip";
                    fi;
                    echo '============'
                done;
            done
        fi
    done
fi

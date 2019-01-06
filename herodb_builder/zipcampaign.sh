#!/usr/bin/env bash
#       sed -i 's/\r$//' zipcampaign.sh


# imports certain functions when running as non-user root
export PATH=$PATH:/sbin

IFS=$'\n'

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`


source "$SCRIPTDIR/config/heroconfdata.sh"


fullpath="$_HEROBACKUPPATH";
droppath="_DROPBOXPATH";


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
    campaignname=$(echo "$target" | grep -oP "(?<=\d\d,\s)\w.*$" | xargs);

    if [ -d "$fullpath/campaigns/$campaignid" ]; then
        newname="${campaignname//[^A-Za-z0-9_]/_}";
	curpath=$(pwd)
	cd "$fullpath"
        zip -r "$fullpath/$newname-$campaignid.zip" "campaigns/$campaignid" > /dev/null;
	cd "$curpath"
        echo "";
        ls -l "$fullpath/$newname-$campaignid.zip";

        for i in $(ls -1 /drives/); do
            if [ -d "/drives/$i/$droppath" ]; then
                if [ -f "/drives/$i/$droppath/$newname-$campaignid.zip" ]; then
                    rm -f "/drives/$i/$droppath/$newname-$campaignid.zip";
                fi;
                mv "$fullpath/$newname-$campaignid.zip" "/drives/$i/$droppath/$newname-$campaignid.zip";
                ls -l "/drives/$i/$droppath/$newname-$campaignid.zip";
            fi;
        done;
    fi;
fi

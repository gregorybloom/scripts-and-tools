#!/bin/bash

SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`

find discordattachments/ -type f >> findall.txt;
rm -f "attachments.txt";
for i in $(cat findall.txt); do
  openstr="https://cdn.discordapp.com/attachments";
  leftoverstr=$(echo "$i" | grep -oP "\/\d+\/\d+\/.*\S");
  echo "$openstr""$leftoverstr" >> "attachments.txt";
done;
rm -f "findall.txt";
find discordavatars/ -type f >> findall.txt;
rm -f "avatars.txt";
for i in $(find discordattachments/ -type f); do
  openstr="https://cdn.discordapp.com/avatars";
  leftoverstr=$(echo "$i" | grep -oP "\/\d+\/.*\S");
  echo "$openstr""$leftoverstr" >> "avatars.txt";
done

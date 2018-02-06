#!/bin/bash
IFS=$'\n'


SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`

source "$SCRIPTDIR/config/autobackup_config.sh"

hasfunct() {
  testfn="$1"
  if [ "$testfn" == "blockid" ]; then
    $(blkid > /dev/null 2>&1)
    if [ "$?" -eq 127 ]; then
      false
    else
      true
    fi
  elif [ "$testfn" == "mail" ]; then
   $(mail > /dev/null 2>&1)
   if [ "$?" -eq 127 ]; then
    false
  else
    true
  fi
elif [ "$testfn" == "swaks" ]; then
 $(swaks --version > /dev/null 2>&1)
 if [ "$?" -eq 127 ]; then
  false
else
  true
fi
fi
}

HAS_SWAKS=true

if ! hasfunct "swaks"; then
  HAS_SWAKS=false
fi


datetime=`date +'%Y-%m-%d - %H:%M %p'`
#test ${#datetime}

if [ "$HAS_SWAKS" == true ] && [ -f "$_HOMEFOLDER/.swaksrc" ]; then
  SWAKUSER=`grep -oP "^\s*--auth-user\s+.*" "$_HOMEFOLDER/.swaksrc"`
  SWAKPASS=`grep -oP "^\s*--auth-password\s+.*" "$_HOMEFOLDER/.swaksrc"`

  SWAKUSER=`echo "$SWAKUSER" | grep -oP "(?<=--auth-user\s).*"`
  SWAKPASS=`echo "$SWAKPASS" | grep -oP "(?<=--auth-password\s).*"`

  SWAKPROTO=`grep -oP "^\s*-s\s+.*" "$_HOMEFOLDER/.swaksrc"`
  SWAKPROTO=`echo "$SWAKPROTO" | grep -oP "(?<=-s\s).*"`

  SWAKFROM=`grep -oP "^\s*--from\s+.*" "$_HOMEFOLDER/.swaksrc"`
  SWAKFROM=`echo "$SWAKFROM" | grep -oP "(?<=--from\s).*"`

  SWAKHFROM=`grep -oP "^\s*h-From\:\s+" "$_HOMEFOLDER/.swaksrc"`
  SWAKHFROM=`echo "$SWAKHFROM" | grep -oP "(?<=h-From\:\s).*"`

  sudo swaks --from "$SWAKFROM" --h-From "$_SWAKHFROM" -s "$SWAKPROTO" -tls -a LOGIN --auth-user "$SWAKUSER" --auth-password "$SWAKPASS" --header "Subject: POWER FAILURE AT $datetime" --body "Power Failed at $datetime" -t "$_ALERTEMAIL"
  echo "sent to $_ALERTEMAIL." | wall
  sleep 15
fi


if echo "$SCRIPTDIR" | grep -qP "^\/media\/\w+\/"; then
  DRIVEPATH=`echo "$SCRIPTDIR" | grep -ioP "^\/media\/\w+\/"`;
  datetimeq=`date +'%Y-%m-%d_%H-%M'`
  FILEPATH="$DRIVEPATH/powerfail-$datetimeq.txt"
  touch "$FILEPATH"
  echo "POWER FAILURE AT $datetime" >> "$FILEPATH"
fi


echo "Power failure imminent!  Try shutdown." | wall
sleep 10
shutdown -h now


if echo "$SCRIPTDIR" | grep -qP "^\/media\/\w+\/"; then
  DRIVEPATH=`echo "$SCRIPTDIR" | grep -ioP "^\/media\/\w+\/"`;
  datetimeq=`date +'%Y-%m-%d_%H-%M'`
  FILEPATH="$DRIVEPATH/powerfail-shutdown0failure-$datetimeq.txt"
  touch "$FILEPATH"
  echo "SHUTDOWN FAILURE AT $datetime" >> "$FILEPATH"
fi

#!/bin/bash
IFS=$'\n'


SCRIPTPATH=`realpath "$0"`
SCRIPTDIR=`dirname "$SCRIPTPATH"`

source "$SCRIPTDIR/config/autobackup_config.sh"
source "$SCRIPTDIR/bash_libs/scrape_swaks.sh"

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
  scrape_swaks_config "$_HOMEFOLDER/"

  sudo swaks --from "$SWAKFROM" --h-From "$_SWAKHFROM" -s "$SWAKPROTO" -tls -a LOGIN --auth-user "$SWAKUSER" --auth-password "$SWAKPASS" --header "Subject: POWER FAILURE AT $datetime" --body "Power Failed at $datetime" -t "$_ALERTEMAIL"
  echo "sent to $_ALERTEMAIL."
  sleep 15
fi


if echo "$SCRIPTDIR" | grep -qP "^\/media\/\w+\/"; then
  DRIVEPATH=`echo "$SCRIPTDIR" | grep -ioP "^\/media\/\w+\/"`;
  datetimeq=`date +'%Y-%m-%d_%H-%M'`
  FILEPATH="$DRIVEPATH/powerfail-$datetimeq.txt"
  touch "$FILEPATH"
  echo "POWER FAILURE AT $datetime" >> "$FILEPATH"
fi


echo "Power failure imminent!  Try shutdown."
sleep 10
shutdown -h now
sleep 10
shutdown -P now


if echo "$SCRIPTDIR" | grep -qP "^\/media\/\w+\/"; then
  DRIVEPATH=`echo "$SCRIPTDIR" | grep -ioP "^\/media\/\w+\/"`;
  datetimeq=`date +'%Y-%m-%d_%H-%M'`
  FILEPATH="$DRIVEPATH/powerfail-shutdown-failure-$datetimeq.txt"
  touch "$FILEPATH"
  echo "SHUTDOWN FAILURE AT $datetime" >> "$FILEPATH"
fi
if [ "$HAS_SWAKS" == true ] && [ -f "$_HOMEFOLDER/.swaksrc" ]; then
  scrape_swaks_config "$_HOMEFOLDER/"

  sudo swaks --from "$SWAKFROM" --h-From "$_SWAKHFROM" -s "$SWAKPROTO" -tls -a LOGIN --auth-user "$SWAKUSER" --auth-password "$SWAKPASS" --header "Subject: SHUTDOWN FAILURE AT $datetime" --body  "SHUTDOWN FAILURE AT $datetime" -t "$_ALERTEMAIL"
  echo "sent to $_ALERTEMAIL."
fi

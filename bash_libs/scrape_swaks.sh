#!/bin/bash
IFS=$'\n'

scrape_swaks_config() {
  SWAKSHOMEFOLDER="$1"
  SWAKUSER=`grep -oP "^\s*--auth-user\s+.*" "$SWAKSHOMEFOLDER/.swaksrc"`
  SWAKPASS=`grep -oP "^\s*--auth-password\s+.*" "$SWAKSHOMEFOLDER/.swaksrc"`

  SWAKUSER=`echo "$SWAKUSER" | grep -oP "(?<=--auth-user\s).*"`
  SWAKPASS=`echo "$SWAKPASS" | grep -oP "(?<=--auth-password\s).*"`

  SWAKPROTO=`grep -oP "^\s*-s\s+.*" "$SWAKSHOMEFOLDER/.swaksrc"`
  SWAKPROTO=`echo "$SWAKPROTO" | grep -oP "(?<=-s\s).*"`

  SWAKFROM=`grep -oP "^\s*--from\s+.*" "$SWAKSHOMEFOLDER/.swaksrc"`
  SWAKFROM=`echo "$SWAKFROM" | grep -oP "(?<=--from\s).*"`

  SWAKHFROM=`grep -oP "^\s*h-From\:\s+" "$SWAKSHOMEFOLDER/.swaksrc"`
  SWAKHFROM=`echo "$SWAKHFROM" | grep -oP "(?<=h-From\:\s).*"`
}

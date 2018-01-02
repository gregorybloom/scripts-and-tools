#!/bin/bash
IFS=$'\n'


for i in $(./autobackup.sh --runtype autoraid --vcheck --email); do
  continue
done

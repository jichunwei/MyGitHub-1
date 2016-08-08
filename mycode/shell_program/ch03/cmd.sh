#!/bin/bash

VAR1=`cat /etc/passwd | awk -F: '{print $1 "\t" $6}'`
echo "VAR1[0]:${VAR1[0]}"
echo "VAR1[1]:${VAR1[1]}"
echo "VAR1[2]:${VAR1[*]}"

VAR2=(`cat /etc/passwd | awk -F: '{pint $1}'`)
echo "VAR2[0]:${VAR2[0]}"
echo "VAR2[1]:${VAR2[1]}"
echo "VAR2[*]:${VAR2[*]}"
exit 0

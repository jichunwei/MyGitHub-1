#!/bin/bash

VAR=`cat /etc/passwd|awk -F: '{print $1 "\t" $6}'`
echo "VAR:$VAR[0]"
sleep  2 

VAR=(`cat /etc/passwd|awk -F: '{print $1 "\t" $6}'`)
echo "VAR:{$VAR[0]"}
exit 0


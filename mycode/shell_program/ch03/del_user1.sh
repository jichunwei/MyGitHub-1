#!/bin/bash

v=${1:?"usage $0 ueser_name"}
home=/home/$v
shell=/bin/bash
name=$v 
var=`cat /etc/passwd |awk -F: {print $1}|grep $v
for v in ${var[]}
do
if [ $v = $var ]
 userdel -r $v
 else
 echo "$v is can not be del"
 fi
 done
 exit 0

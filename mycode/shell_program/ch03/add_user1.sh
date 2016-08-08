#!/bin/bash

v=${1:?"usage $0 #user_name"} 
home=/home/$v
shell=/bin/bash
name=$v
var=`cat /etc/passwd |awk -F: '{print $1}'|grep $v`
for v in ${var[*]}
do
if [ "$v" =  "$var" ]
then
echo "$v can not be added"
exit 1
else
   useradd -m -d $home -s $shell $name
fi
done
exit 0

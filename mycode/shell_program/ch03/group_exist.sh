#!/bin/bash

groupname=${1:?"usage: $0 #name"}

g=`cat /etc/group | awk -F: '{print $1}'`

for v in ${g[*]}
do
if [ "$groupname" = "$v" ]
then
echo " $v is exist"
exit 0 
fi
done


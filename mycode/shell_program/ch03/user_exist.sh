#!/bin/bash

name=${1:?"usage:$0 #username"}

all_name=(`cat /etc/passwd|awk -F: '{print $1}'`)

for v in ${all_name[*]}
do
if [ "$name" = "$v" ]
then
echo "\"$v\""  该用户存在
exit 0
else 
echo "$v is not on"
fi
done

exit 1 

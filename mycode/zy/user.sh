#!/bin/bash

if [ $# -lt 1 ];then

echo "usage: $0 file"
exit 1
fi

export IFS=: 
while read name group   
do
if [ "$name" != ""  ] && [ "$group" != "" ];then

printf "%10s\t%15s\n" $name $group
fi
done < $1
exit 0

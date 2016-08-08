#!/bin/bash

if test $# -lt 1 
then
echo "usage: $0 file"
exit 1
fi


export IFS=:

while read name group
do
print "%10s\t%15\n" $name $group
done< $1
exit 0


#!/bin/bash


VAR=${1:?"usage:$0  #num"}

echo $1 | grep 3 >  /dev/null
if test $? -eq 0 -o  $(($1%3)) -eq 0
then
echo  "$1 is legal num"
else 
echo "$1 is illegal num"
fi
exit 0


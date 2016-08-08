#!/bin/bash

printf "input the file:"
read src_file

printf "input the res file:"
read dest_file
export IFS=:
exec 5<&0
exec 6>&1
exec 0<$src_file
exec 1<$dest_file
while read name pass uid gid desc path shell
do 
printf "$name\t$uid\t$shell";
done
exec 0<&5
exec 1<&6
printf "continue(y/n)"
read yn
if [ "$yn" = "y" ] ||  [ "$yn" = "Y" ]
then
echo "continue"
else 
echo bye
fi
exit 0


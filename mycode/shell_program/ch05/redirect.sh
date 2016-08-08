#!/bin/bash

printf "input the file"
read src_file

printf "input the res file"
read dest_file
export IFS=:
exec 0<$src_file
exec 1<$dest_file
while read name pass uid gid desc path shell
do 
printf "$name\t$uid\t$shell";
done
exit 0


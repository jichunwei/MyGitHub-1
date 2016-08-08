#!/bin/bash

printf "input the file:"
read file_name

printf "input the result file:"
read res_name
export IFS=:
while read name pass uid gid desc path shell 
do
echo -e "$name\t$uid" 1>> $res_name

done 0< $file_name 2> error.txt

exit 0


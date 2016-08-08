#!/bin/bash

name=${1:?"usage:$0 username"}
all_name=`(cat /etc/passwd|awk -F '{print $1}')`
for v in ${all_name[*]}
do
if [ $username = $v ]
then 
exit 0
done
exit

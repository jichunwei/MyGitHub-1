#!/bin/bash

var=${1:?"usage: $0 #username"}
home=/home/$var
shell=/bin/bash
name=$var
if cat /etc/passwd |awk -F: '{print $1}' |grep $var
then 
     userdel -r $var  
exit 0 
else
echo "$var can not del"
fi
exit 1


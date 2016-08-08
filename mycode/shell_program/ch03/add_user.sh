#!/bin/bash

var=${1:?"usage: $0 #user_name"}

home=/home/$var
shell=/bin/bash
name=$var
if  cat /etc/passwd | awk -F: '{print $1}' | grep $var 
then
    echo "$var can not be added"
    exit 1;
else 
    useradd -m -d $home -s $shell $name
fi
exit 0;

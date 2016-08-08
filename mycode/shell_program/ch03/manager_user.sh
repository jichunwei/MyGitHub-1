#!/bin/bash

if [ $UID -ne 0 ]
then
    echo "you are not superuser"
    exit 1 
fi
cmd=${1:?"usage: $0 (add|del) #user"}
name=${2:?"usage: $0 (add|del) #user"}
case $cmd in
    add)
        if  ./add_user.sh $name;then
                 echo "add successful"
        else 
                echo "add failured"
        fi
         ;;
    del)
        if  ./del_user.sh $name ;then
                echo "del successful"
         else 
                echo "del failured"
        fi
        ;;
    *)
        echo "usage:$0 username"
        ;;
esac

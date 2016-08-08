#!/bin/bash

function is_user_exist()
{
    echo "begin function"
    echo "pid: $$"
    echo "a: $0"

    all_names=(`cat /etc/passwd |awk -F: '{print $1}'`)
        for name in ${all_names[*]}
    do 
        if [ "$name" = "$1" ]
            then
                return 0
                fi
                done
                return 1
}
echo "begin manager_user"
set -x
echo "pid: $$"
echo "a: $0"
echo $var
set +x
if is_user_exist $1;then
echo "user:$1 exist"
else
echo "user: $1 does not exist"
fi
exit 0

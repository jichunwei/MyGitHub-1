#!/bin/bash 
if [ $UID -ne 0 ]
then
        echo "you are not superuser"
        exit 1
fi
file=${1:?"usage:$0  filename"}
if [ ! -f $file  ] && [ $file = txt ] 
then
    echo "the file is not exist or is not a txt file!"
    exit 1;
fi
namegroup=(`cat $file`)
    echo $namegroup
for v in ${namegroup[*]}
do
    name=`echo $v |awk -F: '{ print $1 }'`
    group=`echo $v|awk -F: '{ print $2 }'`
    ./user_n_exist.sh $name $group
done
exit 0

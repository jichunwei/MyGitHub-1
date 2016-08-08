#!/bin/bash

shell=/bin/bash
home=/home
create="-m"
while getopts "d:ms:" opt
do
case $opt in
d)
home=$OPTARG
;;
m)
create="-m"
;;
s)
shell=$OPTARG
;;
esac
done

shift $(($OPTIND-1))
name=${1:?"usage: $0 un gn"}
group=${2:-"root"}

if [ ! $UID -eq 0 ]; then
echo "you are not superuser"
exit 1
fi

if ! ./group_exist.sh $group; then
/usr/sbin/groupadd $group
fi

if ./user_exist.sh $name;then
exit 1
else
echo "home:$home"
echo "shell:$shell"
echo "create:$create"
/usr/sbin/useradd -m -d /home/$name -s /bin/bash -g $group $name
echo $name:$name | chpasswd > /dev/null
fi

exit 0

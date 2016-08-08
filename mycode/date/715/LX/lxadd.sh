#!/bin/bash


while getopts "a:bc:" opt
do
case $opt in
a)
echo "-a\$OPTRAG:$OPTARG" ;;
b)
echo "-b\$OPTRAG:$OPTARG" ;;
c)
echo "-c\$OPTRAG:$OPTARG"
;;
?)
echo "error"
exit 1
;;
esac
done


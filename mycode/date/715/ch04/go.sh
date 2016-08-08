#!/bin/bash

#a.sh -c xxx -m -d -p yyy zzz
while getopts "c:mdp:"  opt
do 
case $opt in
c)
echo "c: $OPTARG"
;;
m)
echo "m: no optarg $OPTARG"
;;
d)
echo "d: no optarg $OPTARG"
;;
p)
echo "p: $OPTARG"
;;

esac
done
exit 0

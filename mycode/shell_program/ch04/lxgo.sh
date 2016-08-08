#!/bin/bash

while getopts "a:bc:" opt
do

case $opt in
a)
echo "a: $OPTARG"
;;
b)
echo "b: $OPTARG"
;;
c)
echo "c: $OPTAGR"
;;
esac
done
exit 0

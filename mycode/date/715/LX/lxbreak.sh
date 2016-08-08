#!/bin/bash

for((i=1;i<=10;i++))
do
if [ $i -lt 3 ]
then
continue
fi
if [ $i -gt 7 ]
then
break
fi
echo "$i"
done
exit 0


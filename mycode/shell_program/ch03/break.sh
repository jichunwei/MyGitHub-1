#!/bin/bash

for v in {1..10}
do 
if [ $v -lt 3 ];
then
continue
fi
if [ $v -gt 7 ];then
break
fi
echo "$v"
done
exit 0


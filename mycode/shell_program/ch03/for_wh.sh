#!/bin/bash

x=0
sum=0
for((x=0;x<=100;x++))
do
        x=$(($x+1))
        sum=$(($sum+$x))
done
echo sum is $sum

exit 0


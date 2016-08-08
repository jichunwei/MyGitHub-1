#!/bin/bash

x=0
sum=0
while [ $x -lt 100 ]
do
x=$(($x+1))
   sum=$(($sum+$x))
   done
       echo "sum is $sum" 
#        exit 0



sum=0
for (( i=1;i<=100; i++))
do
   	sum=$(($sum+$i))
done
echo "sum is $sum"

exit 0

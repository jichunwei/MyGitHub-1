#!/bin/bash

sum=0;
for((i=1;i<=100;i++))
        do
        sum=$(($sum+$i))
        done
        echo "sum is $sum"
        
        echo "____________"

        sum=0;
        for i in {1..100}
        do
        sum=`expr $sum + $i`
        done
        echo "sum is $sum"
        exit 0


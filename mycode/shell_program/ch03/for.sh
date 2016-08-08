#!/bin/bash

echo "方法1,C语法结构：----------"

sum=0;
for((i=1;i<=100;i++))
        do
        sum=$(($sum+$i))
        done
        echo "sum is $sum"
        
        echo "_____方法2 for i in {1...100}_______"

        sum=0;
        for i in {1..100}
        do
        sum=`expr $sum + $i`
        done
        echo "sum is $sum"
        exit 0


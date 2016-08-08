#!/bin/bash


$(a=2;b=2;number=`expr $a+$b`;echo $number)
echo $number

${ a=2;b=2;number=`expr $a+$b`; echo $number; }

echo $number


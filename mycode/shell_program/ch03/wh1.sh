#!/bin/bash

x=0
while [ $x -lt 10 ]
do
#	echo $x
x=$(($x+1))
	done
	echo "x is $x"


	echo "------------"
	x=0
	until [ $x -ge 100 ]
	do 
	x=$(($x+1))
sum=$(($sum+$x))
	done
	echo "sum is $sum"    

	echo   "-------------"
	x=0
	until [ $x -ge 10 ]
	do 

x=$(($x+1))
	done
	echo $x

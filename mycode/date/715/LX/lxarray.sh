#!/bin/bash 

echo "the 1 array"
mayvar=("tan 1" "shi 2"  "xiong 3")
echo "tan 1:${mayvar[0]}
echo "shi 2:${mayvar[1]}
echo "xiong 3:${mayvar[2]}"
echo "all:${mayvar[*]}"
echo "all:${mayvar[@]}"

echo "the 2 array"
mayvar=([2]="xiong 3" [0]="tan 1")
echo "tan 1:${mayvar[0]}"
echo "shi 2:${mayvar[1]}"
echo "xiong 3:${mayvar[2]}"
echo "all:${mayvar[*]}"
echo "all:${mayvar[@]}"

echo "the 3 array"
mayvar=([1]="shi 2")
echo "tan 1:${mayvar[0]}"
echo "shi 2:${mayvar[1]}"
echo "all:${mayvar[*]}"
echo "all:${mayvar[@]}"


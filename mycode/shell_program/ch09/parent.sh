#!/bin/bash

echo "parent start"
s=1
./child.sh &
while test   1 -eq 1
do
echo "parent pid: $$ index : $s"
sleep 1
s=$(($s+1))
    done
    echo "parent end"
    exit 0


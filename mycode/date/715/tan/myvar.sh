#!/bin/bash

p1=100
p2=200
p3=$p1+$p2
echo "p3:$p3"
p3=$(($p1+$p2))
echo "p3:$p3"
exit 0

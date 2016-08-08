#!/bin/bash

value="1 2 3 4 100"
for v in $value
do
echo "$v"
done
echo "-------------"

export IFS=:
value="1:2:3:4:100"
for v in $value
do
echo "$v"
done


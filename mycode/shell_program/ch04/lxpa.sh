#!/bin/bash

echo "num:$#"
echo "nr:$*"
echo "pid:$$"


a=0
for v in $*
do
a=$(($a+1))
echo "index:$a $v"
done


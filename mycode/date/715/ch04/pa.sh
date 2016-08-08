#!/bin/bash

echo "parameter num:$#"
echo "parameter: $*"
echo "pid: $$"

start=1
for v in $*
do 
echo "index:$start,$v"
let start=$start+1
done
exit 0


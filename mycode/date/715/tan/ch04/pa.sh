#!/bin/bash

echo "parameter num:$#"
echo "parameter: $*"
echo "pid: $$"

start=1
for v in s*
do 
echo "index:$start,$v"
let start=$start+1
done
exit 0


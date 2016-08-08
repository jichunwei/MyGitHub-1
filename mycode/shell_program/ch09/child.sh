#!/bin/bash

echo "child process start"
start=1
while test $start -lt 10
do
echo "child pid: $$ index: $start"
sleep 1
start=$(($start+1))
    done
    echo "child process end"
    exit 0


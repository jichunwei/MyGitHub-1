#!/bin/bash

function catch_sigint()
{
    printf "catch signal SIGINT"
        trap SIGINT 
}
trap "catch_sigint" SIGINT
trap "" SIGTSTP

start=1
while [ 1 -eq 1 ]
do
echo "index: $start"
sleep 1
start=$(($start+1))
    done

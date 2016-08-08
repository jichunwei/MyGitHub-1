#!/bin/bash

var=${1:?"usage: $0 path"}

if [ -f $var -a $var -a -w $var -a -x $var ];
then
echo "hello"
fi

#!/bin/bash

var=${1:?"usage: $0 #character"}

case $var in
a)
echo "input is a"
;;
b)
echo "input is b"
;;
*)
echo "other character"
;;
esac
exit 0


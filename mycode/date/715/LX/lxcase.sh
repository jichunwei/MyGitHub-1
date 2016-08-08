#!/bin/bash

VAR=${1:?"usage $0 #num"}
case $VAR in
1)
echo "input is 1"
;;
2)
echo "input is 2"
;;

3) echo "input is 3"
;;
*)
echo "input other num"
;;
esac
exit 0


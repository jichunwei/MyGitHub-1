#!/bin/bash

echo "start var2.sh"
echo $$
echo $PPID
echo "NAME_LOCAL:$NAME_LOCAL"
echo "NAME_ENV:$NAME_ENV"
sleep 3
echo "end var2.sh"
exit 0

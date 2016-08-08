#!/bin/bash

echo "start var1.sh"
echo $$
echo $PPID
NAME_LOCAL=kevin
export NAME_ENV=kevin
echo "NAME_LOCAL:$NAME_LOCAL"
ECHO "NAME_ENV:$NAME_ENV"
./var2.sh
echo "end var1.sh"
exit 0

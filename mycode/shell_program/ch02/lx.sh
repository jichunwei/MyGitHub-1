#!/bin/bash
echo "start lx.sh"
echo $$
echo $PPID
NAME_ENV=tanshixiong
export NAME_LOCAL=wanglan
echo "NAME_ENV:$NAME_ENV"
echo "NAME_LOCAL:$NAME_LOCAL" 
./lx1.sh
echo "end lx.sh" 
exit 0


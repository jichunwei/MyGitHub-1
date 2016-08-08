#!/bin/bash

case $1 in
start)
echo "pa start"
./pa.sh tan shi xiong &
echo $! >pa.pid
cat pa.pid
;;
stop)
echo "pa stop"
pid=`(cat pa.pid)`
kill -9 $pid
;;
*)
echo "usage: $0 {start | stop}"
;;
esac
exit 0

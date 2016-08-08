#!/bin/bash

case "$1" in
start)
echo "service start"
./service.sh & 
wait
echo $!  $$  $PPID > service.pid
cat service.pid
;;
stop)
echo "service stop"
pid=(`cat service.pid`)
kill -9 $pid
;;
*)
echo "usage: $0 {start | stop}"
;;
esac
exit 0

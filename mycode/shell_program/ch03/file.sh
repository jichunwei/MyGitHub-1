#!/bin/bash

var=${1:?"usage: $0 #path"}

# -f 文件存在
# -a 逻辑“与”
# -w 可写
# -x 可执行
if [ -f $var -a $var -a -w $var -a -x $var ];

then
echo "hello"
else 
echo "not hello"
fi

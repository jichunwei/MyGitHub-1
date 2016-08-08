#!/bin/bash

var=`echo *`

    select v in ${var[*]}
    do 
    echo $v
#  vi $v
    done
exit 0


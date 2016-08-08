#!/bin/bash

var=`ls`

select v in ${var[*]}
do 
cat $v
done 
exit 0

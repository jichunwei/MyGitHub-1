#!/bin/bash

date
var=`date` 
echo "var:$var"
echo "var[0]:{var[0]}"
echo "var[1]:{var[1]}"

sleep 3
var1=`cat /etc/group |awk -F: '{print $1 "\t" $2}'`
echo "var1[0]:${var1[0]}"
echo "var1[1]:${var1[1]}"
echo "var1[2]:${var1[2]}"
sleep 3

var2=`cat /etc/passwd |awk -F: '{print $1 "\t" $6}'`
echo "var2[0]:${var2[0]}"
echo "var2[1]:${var2[1]}"
echo "var2[5]:${var2[5]}"
echo "var2[*]:${var2[*]}"


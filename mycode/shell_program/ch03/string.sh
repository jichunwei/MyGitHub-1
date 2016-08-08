#!/bin/bash

s1="hello"
if [ $s1 != "hello" ];then
 echo "s1 is not equal to hello "
 else 
 echo "s1 is  equal to hello"
 fi
 s1=
 if [ "$s1" = "hello" ];then
   echo "s1 is equal to hello"
   else 
   echo "s1 is not equal to hello"
   fi 

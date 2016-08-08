#!/bin/bash

echo "--the first array--"
myvar=("first person" "second person" "third person")
echo "first person:${myvar[0]}"
echo "third person;${myvar[2]}"
echo "all persons:${myvar[*]}"
echo "all persons:${myvar[@]}"
echo "--the second array--"
myvar1=([1]=:"third person")
echo "first person: ${myvar1[0]}"
echo "second presho: ${myvar1[1]}"
echo "third person:${myvar1[2]}"
echo "all person:${myvar1[*]}"
echo "all person:${myvar1[@]}"
myvar2=([2]=:"third person")
echo "first person:${myvar2[0]}"
echo "third person: ${myvar2[2]}"
echo "all person:${myvar2[*]}"
echo "all person:${mvary2[@]}"
exit 0

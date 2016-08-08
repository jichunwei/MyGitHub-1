#!/bin/bash


filename=("user1.txt" "user2.txt" "user3.txt")
export IFS=:

while read $filename
do 
case $filename in
user1.txt)
  echo "please input the file: user1.txt"
  ;;
user2.txt)
echo "please input the file:use2.txt"
;;
user3.txt)
echo "please input the file:user3.txt"
;;
*)
echo "error"
;;
esac
done


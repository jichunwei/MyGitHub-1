#!/bin/bash

var="tan shi xiong"

select  v in $var
do 
case $v in
tan)
echo "you choise the tan"
;;
shi)
echo "you choise the shi "
;;
xiong)
echo "you choise the xiong"
;;
*)
echo "error choise"
esac
done


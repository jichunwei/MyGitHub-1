#!/bin/bash

var="c1 c2 all none"
select c in $var
do
case $v in
c1)
echo you choise is c1;;
c2)
echo you choise is c2;;
all)
echo "you choise is c1 c2";;
none)
break;;
*)
echo "error";;
esac
done

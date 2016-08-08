#!/bin/bash

VAR=${PAR:+"hello world"}
echo "PAR:$PAR, VAR:$VAR"

PAR=
set |grep PAR
VAR=${PAR:="hello world"}
echo "PAR:$PAR, VAR:$VAR"

PAR="hello  shell"
set |grep PAR
echo "PAR:$PAR, VAR:$VAR"
VAR=${PAR:="hello world"}

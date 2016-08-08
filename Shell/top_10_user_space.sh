#!/bin/bash
#
#Big_Users -fid big disk space users in various directories
####################################################
#Parameters for Script
#
CHECK_DIRECTORIES=" /var/log /home/"  
#
####################################################
#
DATE=$(date '+%m%d%y')
echo $DATE
#
exec > disk_space_$DATE.rpt
#
echo "Top Ten Disk Space Usage"
echo "for $CHECK_DIRECTORIES Directories"
#
for DIR_CHECK in $CHECK_DIRECTORIES
do 
	echo ""
	echo "The $DIR_CHECK Directory:"
#
#Create a listing of top ten disk space users
du -S $DIR_CHECK 2>/dev/null | sort -rn | sed '{11,$D;=}' | sed 'N; s/\n/ /' | gawk '{printf $1 ":" "\t" $2 "\t" $3 "\n"}'
#du -S $DIR_CHECK 2>/dev/null | sort -rn | sed '{11,$D;=}' | sed 'N; s/\n/ /'
#
done
#

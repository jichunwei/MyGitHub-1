#!/bin/bash

#Daily_Arichive - Archive designated files & directors
######################################################
#
#Gather currenet Date
#
DATE=`date +%y%m%d`
#
#Set Archive File Name
#
FILE=archvie$DATE.tar.gz
#
#Set configuration and Destination File
#
CONFIG_FILE=/home/user/archvie/Files_To_Backup
DESTINATION=/home/user/archvie/$FILE
#
##############Main Script#########################
#
#Check Backup config file exists
#
if [ -f $CONFIG_FILE ] 
then
	echo 
else
	echo 
	echo "$CONFIG_FILE does not exists"
	echo "Backup not completed due to missing Configuration file"
	echo 
	exit
fi 
#
#Build the names of all the files to backup
#
#FILE_NO=1
exec < $CONFIG_FILE
#
read FILE_NAME
#
while [ $? -eq 0 ]
do
	if [ -f $FILE_NAME -o -d $FILE_NAME ]
	then
		FILE_LIST="$FILE_LIST $FILE_NAME"
	else
		echo 
		echo "$FILE_NAME, does not exists"
		echo "Obviously. I will not include it in this  archive"
		echo "It is listed on line $FILE_NO of the config file."
		echo "Continuing to build archive list ..."
		echo 
	fi 	
#
	FILE_NO=$[FILE_NO + 1]
	read $FILE_NAME
done
#
####################################
#
#Backup the files and compress Archive
#
tar -czf $DESTINATION $FILE_LIST 2>/dev/null
#


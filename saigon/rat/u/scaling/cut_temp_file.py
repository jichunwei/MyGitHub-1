#######################################################
#
# Script: cut_temp_file.py
# Author: Webber Lin
# Purpose: Cut the FM user information file into 20 files
#######################################################
import os
import sys
#filename="C:\\FM\\FM_saigon\\saigon_49189\\rat\\temp.txt"
def getFileName(filename='temp.txt'):
	return os.getcwd()+"\\%s" % filename

def usage():
	print "python cut_temp_file.py [filename] [items_per_file] [te_id_start] [te_id_end]"
	print "example: python cut_temp_file.py temp.txt 5 8 27"

if __name__ == '__main__':

	if len(sys.argv) < 5:
		usage()
		exit(1)
	fname=sys.argv[1]
	items_per_file=sys.argv[2]
	te_start=sys.argv[3]
	te_end=sys.argv[4]
	filename=getFileName(fname)
	
	#read from input
	print "FileName:%s\nUserInformation/page:%s\nTestEngine_ID:%s~%s" %(fname,items_per_file,te_start,te_end)
		
	file_handler=open(filename,'r')
	file_contents=file_handler.readlines()
	total_lines_num=len(file_contents)	
	pages=total_lines_num/int(items_per_file)
	#debug information
	print "\n\ntotal_lines_num: %s " % total_lines_num
	print "items_per_file:%s" % items_per_file
	print "Pages will be created: %s " % pages

	items_for_each_page=[file_contents[i*int(items_per_file):i*int(items_per_file)+int(items_per_file)] for i in xrange(pages)]
	#for item in items_for_each_page:
		#for i in item:
		#	print i
		#print "---------------------"

	#idea: 
	# 1. split a text file to sub txt files
	# 2. slice a list to sub lists
	count=int(te_start)    
	cwd=os.getcwd()
	
	#goTo destination or create a directory
	try:
		os.mkdir(cwd+"\\te_information")
	except:
		os.chdir(cwd+"\\te_information")
	
	for item in items_for_each_page:
		if count <= int(te_end):
			print "File created: sf_%s.txt" % count
			sf=open("%s\\te_information\\sf_%s.txt" % (cwd,count),'w')
			for it in item:
				sf.write(it)
			count=count+1
			sf.close()
			

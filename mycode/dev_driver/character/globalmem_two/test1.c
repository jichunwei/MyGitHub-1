#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <string.h>

int main(int argc ,char *argv[])
{
	int fd;
	
	if(argc != 2){
		fprintf(stderr,"usage,%s\n",argv[0]);
		exit(1);
	}
	if((fd = open(argv[1],O_RDWR)) < 0){
		perror("open");
		exit(1);
	}
	char *info = "welcome to briup!\n";
	int len = strlen(info);
	if(write(fd,info,len) < 0){
		perror("write error!\n");
		exit(EXIT_FAILURE);
	}
	close(fd);
	return 0;
}

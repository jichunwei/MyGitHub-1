#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>

#define MAXSIZE		100

int main(int argc ,char *argv[])
{
	int		fd;

	if(argc != 2){
		fprintf(stderr,"-usage:%s \n",argv[0]);
		exit(1);
	}
	if((fd = open(argv[1],O_RDWR)) < 0){
		perror("open file error!\n");
		exit(EXIT_FAILURE);
	}
	char buf[MAXSIZE];
	memset(buf,0,MAXSIZE);
	if(read(fd,buf,MAXSIZE) <0){
		perror("read");
		exit(EXIT_FAILURE);
	} 
	printf("buf:%s\n",buf);
	close(fd);
	return 0;
}

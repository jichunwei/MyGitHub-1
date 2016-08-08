#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>

#define MEM_CLEAR	1

int main(int argc ,char *argv[])
{
	int		fd;

	if((fd = open(argv[1],O_RDWR)) < 0){
		perror("open");
		exit(EXIT_FAILURE);
	}
	long p1 = lseek(fd,0,SEEK_CUR);
	printf("p1:%ld\n",p1);
	long p2 = lseek(fd,10,SEEK_SET);
	printf("p2:%ld\n",p2);
	long p3 = lseek(fd,2049,SEEK_SET);
	printf("p3:%ld\n",p3);

	if(!ioctl(fd,MEM_CLEAR))
		printf("memory clear succcess!\n");
	
	close(fd);
	return 0;
}

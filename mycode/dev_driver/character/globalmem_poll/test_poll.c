#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

#define	MEM_CLEAR	1
int main(int argc ,char *argv[])
{
	int		fd;
	fd_set	rfds,wfds;

	if((fd = open(argv[1],O_RDWR)) < 0){
		perror("open file error!\n");
		exit(EXIT_FAILURE);
	}
	if(ioctl(fd,MEM_CLEAR) < 0){
		perror("ioctl error!\n");
	}
	while(1){
		FD_ZERO(&rfds);
		FD_ZERO(&wfds);
		FD_SET(fd,&rfds);
		FD_SET(fd,&wfds);
		select(fd + 1,&rfds,&wfds,NULL,NULL);
		if(FD_ISSET(fd,&rfds))
			printf("poll monitor,can be read!\n");
		if(FD_ISSET(fd,&wfds))
			printf("poll monitor,can be written!\n");
		sleep(1);
	}
	return 0;
}

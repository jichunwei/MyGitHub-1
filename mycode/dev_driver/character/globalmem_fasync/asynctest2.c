#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <signal.h>

#define		MAXSIZE	100

int		fd;
void signal_handler(int signo)
{
	char	buf[MAXSIZE];
	int		nread;

	memset(buf,0,MAXSIZE);
	nread = read(fd,&buf,MAXSIZE);
	printf("input can be used,buf:%s\n",buf);
}

int main(int argc ,char *argv[])
{
	int		oldflags;

	if(signal(fd,signal_handler) < 0){
		perror("signal error!\n");
	}
	if((fd = open(argv[1],O_RDWR)) < 0){
		perror("open error!\n");
		exit(EXIT_FAILURE);
	}

	fcntl(fd,F_SETOWN,getpid());
	oldflags = fcntl(fd,F_GETFL);
	fcntl(fd,F_SETFL,oldflags|FASYNC);
	while(1);

}


#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <signal.h>

#define		MAXSIZE	100

void signal_handler(int signo)
{
	char	buf[MAXSIZE];
	
	memset(buf,0,MAXSIZE);
	if(signo == SIGIO){
		int  nread;
		nread = read(STDIN_FILENO,buf,MAXSIZE);
		if(nread  > 0){
			printf("input can be used,buf:%s\n",buf);
		}
	}
}

int main()
{
	int		oldflags;

	if(signal(SIGIO,signal_handler) == SIG_ERR){
		perror("signal error!\n");
	}
	fcntl(STDIN_FILENO,F_SETOWN,getpid());
	oldflags = fcntl(STDIN_FILENO,F_GETFL,0);
	fcntl(STDIN_FILENO,F_SETFL,oldflags | FASYNC);
	while(1);
}


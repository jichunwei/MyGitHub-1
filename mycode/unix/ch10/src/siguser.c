#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>

static void sig_handler(int signo)
{
	if(signo == SIGUSR1){
		printf("siguser1 received\n");
	}else if (signo == SIGUSR2){
		printf("siguser2 received\n");
	}else 
		printf("received signo:%d\n",signo);
}

int main(void)
{
	if(signal(SIGUSR1,sig_handler) == SIG_ERR){
		perror("signal siguser1 error");
		exit(1);
	}else if(signal(SIGUSR2,sig_handler) == SIG_ERR){
		perror("signal siguser2 error");
		exit(1);
	}
	while(1)
		pause();
}

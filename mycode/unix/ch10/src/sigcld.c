#include <unistd.h>
#include <errno.h>
#include <sys/wait.h>
#include <string.h>
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>

static void sig_chld(int signo)
{
	pid_t	pid;
	int		status;

	printf("SIGCLD recevide\n");
	if(signal(SIGCLD,sig_chld) == SIG_ERR){
		perror("signal");
		exit(1);
	}
	if ((pid = wait(&status)) < 0){
		perror("wait");
		exit(1);
	}
	printf("pid = %d\n",pid);
}

int main(void)
{
	pid_t	pid;

	if(signal(SIGCLD,sig_chld) == SIG_ERR){
		perror("signal error");
		exit(1);
	}
	if((pid = fork()) < 0){
		perror("fork");
		exit(1);
	}else if (pid == 0){
		sleep(2);
		_exit(0);
	}
	pause();
	exit(0);
}

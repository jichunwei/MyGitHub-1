#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

static void sig_handler(int signo)
{
	printf("SIGHUP ecurred ,pid = %d\n",getpid());
}

static void pr_process(char *name)
{
	printf("%s: pid = %d,ppid = %d,pgid = %d,pgrp = %d,tpgrp = %d\n",name,getpid(),getppid(),getpgrp(),
			tcgetpgrp(STDIN_FILENO));	
	fflush(stdout);
}

int main()
{
	char	c;
	pid_t	pid;
	
	pr_process("parent");
	if((pid = fork()) < 0){
		perror("fork");
		exit(1);
	}else if(pid > 0){
		sleep(3);
		exit(0);
	}else {
		pr_process("child");
		if(signal(SIGHUP,sig_handler) < 0){
			perror("signal");
			exit(1);
		}
		kill(getpid(),SIGTSTP);
		pr_process("child");
		if(read(STDIN_FILENO,&c,1) != 1){
			printf("read error from controling TTY, errno = %d\n", errno);
		}
	}
	exit(0);
}

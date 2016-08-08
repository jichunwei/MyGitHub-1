#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(void)
{
	pid_t		pid;
	int			pgid;
	
	pid = fork();
	pgid = setpgid(pid,pid);
	if(pgid < 0){
		perror("setpgid");
		exit(1);
	}
//	printf("pid:%d,pgid:%d\n",getpid(),getpgid());
	if(pid < 0){
		perror("fork");
		exit(1);
	}else if(pid == 0){
	//	printf("pid:%d,pgid:%d\n",getpid(),getpgid());
		if((pid = fork()) < 0){
			perror("fork1");
			exit(1);
		}else if(pid == 0){
			setpgid(getpid(),pgid);
			printf("pid:%d,pgid:%d\n",getpid(),getpgid());
		}
		wait(NULL);
	}
	wait(NULL);
	return 0;
}

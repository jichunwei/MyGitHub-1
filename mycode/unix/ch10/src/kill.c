#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(void)
{
	pid_t		pid;
	int			pgid;

	//	if((pid = fork()) < 0){
	//		perror("fork");
	//		exit(1);
	//	}
	pgid = setpgid(getpid(),getpgid());
	printf("pid:%d,pgid:%d\n",getpid(),getpgid());
	printf("==============\n");
	int i = 0;
	for(; i < 2; i++){
		pid = fork();
		if(pid > 0)
			return -1;
	}
	//setpgid(getpid(),pgid);
	printf("pid:%d,pgid:%d\n",getpid(),getpgid());

	return 0;
}

// 创建会话，其调用进程必须是非进程组进程、若是，则返回出错（-1);
#include <unistd.h>
#include <error.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main()
{
	pid_t	pid;
	
//	pid = setsid();
//	printf("session id:%d\n",pid);
	if((pid = fork()) < 0){
		perror("fork");
		exit(1);
	}
	if(pid == 0)
		pid = setsid();
	else if(pid > 0)
		exit(0);
	printf("session id:%d\n",pid);
	return 0;
}

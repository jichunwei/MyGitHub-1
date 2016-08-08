#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
	pid_t		pid;
	int			fd;
	int			p;

	if( argc != 2){
		fprintf(stderr,"-usage:%s\n",argv[0]);
		exit(1);
	}
	fd = open(argv[1],O_RDONLY);
	if (fd < 0){
		perror("open");
		exit(1);
	}
	//若成功则返回前台进程组的进程id,若出错则返回－1；
	pid = tcgetpgrp(fd);
	printf("pro_process id:%d\n",pid);

	//设置前台进程组id,成功则返回0，出错则返回－1
	if((p = tcsetpgrp(fd,getpid())) < 0){
		perror("tcsetpgrp");
		exit(1);
	}
	printf("pro_process id:%d\n",getpid());
	//获取会话进程id，成功则返回会话首进程的进程组id，出错返回－1；
	pid = tcgetsid(fd);
	printf("pro_process id:%d\n",getpid());
	return 0;
}

#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(int argc ,char *argv[])
{
    if(argc < 3)
    {
        fprintf(stderr,"-usage:%s file1,file2\n",argv[0]);
        exit(1);
    }
    pid_t pid;
    if((pid = fork()) < 0){
        perror("fork");
    }else if(pid == 0)
    {
        int fd1 = open(argv[1],O_WRONLY|O_CREAT|O_TRUNC, S_IRWXU|S_IRWXG|S_IRWXO);
        int fd2 = open(argv[2],O_WRONLY|O_CREAT|O_TRUNC, S_IRWXU|S_IRWXG|S_IRWXO);
        if(fcntl(fd1,F_SETFD,0) < 0){
            perror("fcntl_fd1");
        }
        if(fcntl(fd2,F_SETFD,1) < 0){
            perror("fcntl_fd2");
        }
        char a1[20],a2[20];
        memset(a1,0,2);
        memset(a2,0,2);
        sprintf(a1,"%d",fd1);
        sprintf(a2,"%d",fd2);
        printf("fd1:%d a1;%s fd2:%d a2:%s\n",fd1,a1,fd2,a2);
        if(execlp("./bin/exec_file","./bin/exec_file",a1,a2,NULL) < 0)
        {
            perror("execlp");
            exit(127);
        }
    }
    printf("------finished--------\n");
    return 0;
}


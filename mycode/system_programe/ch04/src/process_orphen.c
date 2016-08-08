#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    pid_t pid;
    if((pid = fork()) < 0)
    {
        perror("fork");
    }
    else if(pid > 0){
        //parent process
        sleep(1);
    }
    else{
    printf("pid:%d,ppid:%d\n",getpid(),getppid());
    }
    if(pid > 0)
    {
        exit(0);
    }else
    {
        sleep(2);
    printf("pid:%d,ppid:%d\n",getpid(),getppid());
    };
    exit(0);
}


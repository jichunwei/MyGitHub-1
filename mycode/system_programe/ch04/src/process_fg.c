#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    if(setpgid(getpid(),getppid()) < 0)
    {
        perror("setpgid");
    }
    pid_t pid;
    int i = 1;
    for(; i <= 2; i++)
    {
        pid = fork();
        if(pid < 0)
        {
            perror("fork");
        }
        else if(pid == 0)
        {//child process
            if(setpgid(getpid(),getpid()) < 0)
            {
                 perror("setpgid");
        }
            if(i == 1)
            {
                if(tcsetpgrp(0,getpgid(getpid())) < 0)
                    perror("tcsetpgrp");
            }
            break;
        }
        else {//parent process
            if(setpgid(pid,pid) < 0){
                perror("setpgid");
        }
            if(i == 1)
            {
                if(tcsetpgrp(0,getpgid(pid))< 0)
                    perror("tcsetpgrp");
            }
    }
    }
    printf("pid:%d ppid:%d pgid :%d\n",getpid(),getppid(),getpgid(0));
    sleep(1);
    printf("waitingt for control signal\n");
    pause();
    exit(0);
}

#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    int i = 1;
    if(setpgid(getpid(),getpid()) < 0)
    {
        perror("setpgid");
    }
    pid_t g1 = getpgid(0);
    pid_t pid;
    for(; i <= 2; i++)
    {
        pid = fork();
        if((i == 1) && (pid == 0)){//child(p1)
            setpgid(getpid(),getpid());
        }else if(pid > 0){//parent(p)
            setpgid(pid,pid);
            break;
        }
        if(( i == 2) && (pid == 0)) {//child(p2)
            setpgid(getpid(),g1);
            break;
        }
        else if(pid > 0){//child(p1)
            setpgid(pid,getpgid(getppid()));
        }
    }
    printf("i:%d,pid:%d ppid:%d pgid:%d\n",i,getpid(),getppid(),getpgid(0));
    return 0;
}







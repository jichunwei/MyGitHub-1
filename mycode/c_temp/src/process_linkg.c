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
    for(; i <= 3; i++)
    {
        pid = fork();
        if(pid == 0){
            break;
        }
        if((i == 1) &&(pid == 0))
        {
            setpgid(getpid(),getpid());
        }
        else if(pid > 0){
            setpgid(pid,pid);
        }
        //    pid_t g2 = getpgid(pid);
        if((i == 2) &&(pid == 0))
        {
            setpgid(getpid(),getpid());
        }
            pid_t g2 = getpgid(pid);
        if((i == 3) && (pid == 0))
        {
            setpgid(pid,g2);
        }
       
    }
        printf("i:%d,pid:%d,ppid:%d,pgid:%d,\n",i,getpid(),getppid(),getpgid(0));
        sleep(5);
        exit(0);
}
        

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

int main()
{
    int i = 0;
    pid_t pid;
    setpgid(pid,pid);
    pid_t g1;
    getpgid(getpid()) ==  g1;
    for(; i <= 2; i++)
    {
        pid = fork();
        if(pid == 0)
        break;
    setpgid(getpid(),g1);
    printf("%d,0x%p,0x%p\n",i,getpid(),getppid());
    }
    return 0;
}

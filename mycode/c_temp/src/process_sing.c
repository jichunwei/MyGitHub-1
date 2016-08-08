#include <stdio.h>
#include <stdlib.h>

int main()
{
    int i = 1;
    pid_t pid;
    for(; i < 5; i++)
    {
       pid = fork();
        if(pid == 0)
            break;
    }
    printf("i:%d,pid:%d,ppid:%d\n",i,getpid(),getppid());
    sleep(5);
    printf("\n");
    exit(0);
}

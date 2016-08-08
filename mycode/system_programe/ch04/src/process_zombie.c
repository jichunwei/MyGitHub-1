#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    pid_t pid;
    if((pid = fork())< 0){
        perror("fork");
    }
    else if(pid == 0){
        exit(0);
    }
    printf("pid:%d,ppid:%d\n",getpid(),getppid());
    while(1){}
    exit(0);
}

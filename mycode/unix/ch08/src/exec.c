#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>

char     *env_init[] = {"USER=unkown","PATH=/tmp",NULL};

int main()
{
    pid_t   pid;
    
    pid = fork();
    if(pid < 0){
        perror("fork");
    } else if (pid == 0){
        if(execle("/home/tan/unix/ch08/bin/fork","fork",(char*)0,env_init) < 0)
            perror("execle");
        
    }
    
    if(waitpid(pid,NULL,0) < 0){
        perror("waitpid");
    }
    
    if((pid = fork()) < 0)
        perror("fork");
    else if (pid == 0){
        if (execlp("/home/tan/unix/ch08/bin/fork", "fork", "only a arg", (char *)0) < 0)
            perror("execlp");
    }
    exit(0);
}


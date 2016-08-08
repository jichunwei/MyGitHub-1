#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    pid_t   pid;

    pid = fork();
    if(pid < 0){
        perror("fork");
        exit(1);
    }
    else if (pid == 0){
        if(execl("/home/tan/unix/ch08/bin/testinterp","testinterp","myarg1","myarg2",(char *)0) < 0){
            perror("execl");
            exit(1);
        }
    }
    if(waitpid(pid,NULL,0) < 0){
        perror("wait");
        exit(1);
    }
    exit(0);

}

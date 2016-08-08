#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#define  MAXSIZE 1024

int main()
{
    int         fd[2];
    pid_t       pid;
    ssize_t     size;
    char        buffer[MAXSIZE];

    if(pipe(fd) < 0){
        perror("pipe");
        exit(1);
    }
    pid = fork();
    if(pid < 0){
        perror("fork");
    }else if(pid > 0){
        close(fd[0]);
        write(fd[1],"hello tan!\n",10);
        close(fd[1]);
    }else{
        close(fd[1]);
        size = read(fd[0],buffer,MAXSIZE);
        write(1,buffer,size);
        printf("\n");
        close(fd[0]);
    }
    exit(0);
}
        


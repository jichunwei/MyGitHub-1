#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#define MAXLINE 1024

int main()
{
    int fd[2];
    int n;
    pid_t pid;
    char line[MAXLINE];
    if(pipe(fd) < 0){
        perror("pipe");
    }
    pid = fork();
    if(pid < 0){
        perror("fork");
    }
    else if(pid > 0){
        close(fd[0]);
        if((write(fd[1],"hello world!\n",12)) != 12){
            perror("write");
        }
        close(fd[1]);
    }else
    {
        close(fd[1]);
  //      if((read(fd[0],line,MAXLINE)) < 0){
   //         perror("read");
    //    }
        n = read(fd[0],line,MAXLINE);
        write(STDOUT_FILENO,line,n);
        close(fd[0]);
    }
    exit(0);
}



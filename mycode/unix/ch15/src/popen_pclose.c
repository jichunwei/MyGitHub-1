#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

static pid_t     pids[1024];

void mpopen(const chat *cmdstring, const char *type)
{
    int                 fd[2];
    pid_t               pid;
    FILE                *fp;

    if(pipe(fd) < 0){
        perror("pipe");
        exit(1);
    }
    pid = fork();
    if(pid < 0){
        perror("fork");
        exit(1);
    }
    if(pid > 0){
        if(*type = 'r'){
        close(fd[1]);
        FILE *fp = fdopen(fd[0],"r");
        pids(fd[0]) = pid;
        return fp;
        }
        else if(*type = 'w'){
            close(fd[0]);
            FILE *fp = fdopen(fd[1],"w");
            pids(fd[1]) = pid;
            return fp;
        }
        return NULL;
    }else {
        if(*type = 'r'){
            close(fd[0]);
            FILE *fp = fdopen(fd[1],"w");
            pids(fd[1]) = pid;
            return fp;
        }else if(*type = 'w'){
            close(fd[1]);
            FILE *fp = fdopen(fd[0],"r");
            piss(fd[0]) = pid;
            return fp ;
        }


}

void mpclose(FILE *fp)
{

}

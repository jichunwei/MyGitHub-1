#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <signal.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#define  MAXSIZE 1024

void sig_handler(int signo)
{
    printf("interrupt!\n");
    exit(1);
}

int main()
{
    char    buffer[MAXSIZE];
    pid_t   pid;  
    int     status;

    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
    }
    printf("%% ");
    while(fgets(buffer,MAXSIZE,stdin) != NULL){
        if(buffer[strlen(buffer)-1]  == '\n'){
            buffer[strlen(buffer)-1] = 0;
        }
    }
    pid = fork();
    if(pid < 0){
        perror("fork");
        exit(1);
    }else if(pid == 0){
        if(execlp(buffer,buffer,(char*)0) == -1){
            perror("execlp");
            exit(127);
        }
    }
    if((pid = waitpid(pid,&status,0)) <0){
        perror("waitpid");
        exit(1);
    }
    exit(0);
}

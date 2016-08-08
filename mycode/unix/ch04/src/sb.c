#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

void sig_handler(int signo)
{
    if(signo == SIGINT){
        printf("interupt occured!\n");
        exit(0);
    }
}

int main()
{
    int     fd;
    char    buffer[] = "徐宏是傻比!" ;

    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    while(1){
        if(write(STDOUT_FILENO,buffer,sizeof(buffer)) < 0){
            perror("write");
            exit(1);
        }
        printf("\n");
    }
    exit(0);
}

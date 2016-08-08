#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>

void sig_handler(int signo)
{
    if(SIGINT == signo)
    {
        printf("SIGINT occured\n");
    }
    if(SIGTSTP == signo)
    {
        printf("SIGTSTP occured\n");
    }
    sleep(5);
    printf("sig_handler finished\n");
}

int main()
{
    if(signal(SIGINT,sig_handler)){
        perror("signal");
    }
    if(signal(SIGTSTP,sig_handler)){
        perror("signal");
    }
    printf("begin running\n");
    while(1)pause();
    printf("end running\n");
    exit(0);
}


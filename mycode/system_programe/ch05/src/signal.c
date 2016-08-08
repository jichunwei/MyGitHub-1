#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

void sig_handler(int signo)
{
    if(SIGINT == signo){
        printf("you can not interrupt me! %d\n",signo);
    }
        printf("you can not interrupt me! %d\n",signo);
        if(SIGUSR1 == signo)
        {
            printf("SIGUSR1 interrupt me! %d\n",signo);
            exit(0);
    }
}

int main()
{
    if((SIGTSTP,SIG_IGN)==SIG_ERR)
    {
       perror("signal(SIG_IGN)");
       exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR)
    {
        perror("signal(SIGINT)");
        exit(1);
    }
    if(signal(SIGUSR1,sig_handler) == SIG_ERR)
    {
        perror("signal(SIGUSR1)");
        exit(1);
    }
    printf("waiting for signal\n");
    int i = 1;
    while(1){
        printf("pid %d output %d\n",getpid(),i);
        i++;
        sleep(1);
    }
    exit(0);
}



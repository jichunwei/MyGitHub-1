#include <signal.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

void sig_handler(int signo)
{
    if(SIGTSTP == signo)
    {
        printf("SIGTSTP occured\n");
    }
}

void cal_fun(void)
{
    printf("begin running cal_fun\n");
    sleep(10);
    printf("end running cal_fun\n");
}

int main()
{
    if(signal(SIGTSTP,sig_handler) == SIG_ERR)
    {
        perror("signal");
    }
    printf("begin running main\n");
    cal_fun();
    printf("end running main\n");
    exit(0);
}


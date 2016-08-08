#include <signal.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

void sig_handler(int signo)
{
    if(SIGALRM == signo)
    {
        printf("clock time out\n");
        alarm(5);
        }
}

void gener_data()
{
    int i=1;
    while(1){
        double d = drand48();
        printf("%10d:%1f\n",i++,d);
        sleep(1);
    }
}

int main()
{
    if(signal(SIGALRM,sig_handler) == SIG_ERR)
    {
        perror("signal");
    }
    alarm(5);
    printf("begin running main\n");
    gener_data();
    printf("end running main\n");
    exit(0);
}


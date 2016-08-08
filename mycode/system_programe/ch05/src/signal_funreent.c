#include <signal.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>


int g_v[10];
int *h_v;

void user_call(int v)
{
    int a_v[10];
    int i = 0;
    sigset_t set;
    sigfillset(&set);
    if(sigprocmask(SIG_SETMASK ,&set,NULL) < 0)
    {
        perror("sigprocmask");
    }
    for(; i < 10; i++)
    {
        a_v[i] = v;
        g_v[i] = v;
        h_v[i] = v;
        sleep(1);
    }
    sigemptyset(&set);
    if(sigprocmask(SIG_SETMASK ,&set,NULL) < 0)
    {
        perror("sigprocmask");
    }
    printf("g_v:");
    for(i = 0; i < 10; i++){
        if(i != 0)printf(",%d",g_v[i]);
        else printf("%d",g_v[i]);
    }
    printf("\n");
    printf("h_v:");
    for( i = 0; i < 10; i++)
    {
        if(i != 0)printf(",%d",h_v[i]);
        else printf("%d",h_v[i]);
    }
    printf("\n");
    printf("a_v");
    for( i = 0; i < 10; i++)
    {
        if(i != 0)printf(",%d",a_v[i]);
        else printf("%d",a_v[i]);
    }
    printf("\n");
}

void signal_handler(int signo)
{
    if(SIGTSTP == signo)
    {
        printf("SIGTSTP occured\n");
        user_call(10);
    }
}

int main()
{
    if(signal(SIGTSTP,signal_handler) == SIG_ERR)
    {
        perror("signal");
    }
    h_v = (int *)calloc(10,sizeof(int));
    printf("begin running main\n");
    user_call(20);
    printf("end running main\n");
    exit(0);
}
    


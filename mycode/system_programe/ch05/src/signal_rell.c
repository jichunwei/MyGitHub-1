#include <unistd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int  is_sig_occ = 0;
void sig_handler(int signo)
{
    printf("signo occured:%d\n",signo);
    is_sig_occ = 1;
}

int main()
{
    if(signal(SIGINT, sig_handler) == SIG_ERR)
    {
        perror("signal");
    }
    printf("begining running\n");
    while(is_sig_occ == 0)
    {
        sleep(3);
        pause();
    }
    printf("ok,i will go running\n");
   return 0;
}

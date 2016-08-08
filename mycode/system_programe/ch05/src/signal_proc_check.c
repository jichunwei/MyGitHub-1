#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <errno.h>

void out_set(sigset_t set,char *s)
{
    int  i = 1;
    int  k = 0;
    for(; i <= 31; i++)
    {
        if(sigismember(&set,i)){
            k++;
            printf("%d was %s\n",i,s);
        }
    }
    if(k == 0) printf("no signal was %s\n",s);
}

void sig_handler(int signo)
{
    printf("begin process %d\n",signo);
    sigset_t    nset,oset;
    sigemptyset(&oset);
 /*   sigemptyset(&nset);
    if((sigprocmask(SIG_SETMASK,&nset,&oset)) < 0)
    {
        perror("sigprocmask");
    }
    */
    out_set(oset,"masked");
    printf("%d occured\n",signo);
    sleep(10);
    sigemptyset(&oset);
    if((sigpending(&oset)) < 0){
        perror("sigpending");
    }
        out_set(oset,"pended");
    printf("end process %d\n",signo);
}
            
int main()
{
    sigset_t oset;
    sigemptyset(&oset);
    if((sigprocmask(SIG_BLOCK,NULL,&oset)) < 0){
        perror("sigprocmask");
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR)
    {
        perror("signal");
    }
    printf("begin running main\n");
    out_set(oset,"masked");
    pause();
    sigemptyset(&oset);
    if((sigprocmask(SIG_BLOCK,NULL,&oset)) < 0){
        perror("sigprocmask");
    }
    out_set(oset,"masked");
    exit(0);
}


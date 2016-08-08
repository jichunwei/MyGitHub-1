#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

static void
my_alarm(int signo)
{
    struct passwd *rootp;
    printf("in signal handler\n");
    if((rootp = getpwnam("root")) == NULL)
        perror("getpwnam(root) error");
    alarm(1);
    return;
}
int main()
{
    struct passwd *p;
    signal(SIGALRM ,my_alarm);
    alarm(1);
    for(; ;){
        if((p = getpwnam("stevens")) == NULL)
            perror("getpwnam error");
        if(strcmp(p->pw_name,"stevens") != 0)
            printf("return value corrupterd !,pw_name= %s\n",
        p->pw_name);

    }
}


        

#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <stdio.h>

void pr_exit(int status)
{
    if(WIFEXITED(status)){
        printf("normal termination,exit status = %d\n",
                WEXITSTATUS(status));
    }else if(WIFSIGNALED(status)) {
        printf("abnormal termiantion,exit status = %d\n",
                WTERMSIG(status),
#ifdef  WCREDUMP
                WCOREDUMP(status) ? "(core file getnerate)": "");
#else
        "");
#endif
    }
    else if(WIFSTOPPED(status)){
            printf("child stopped,signal number = %d\n",WSTOPSIG(status));
    }
}

int main()
{
    int status;

    if((status = system("date")) < 0){
        perror("system");
        exit(1);
    }
    pr_exit(status);
    if((status = system("nosuchcomand")) < 0){
        perror("systemno");
        exit(1);
    }
    pr_exit(status);
    if((status = system("who; exit 44")) < 0){
        perror("systemexit");
        exit(1);
    }
    pr_exit(status);
    return 0;
}

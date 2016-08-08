#include <sys/wait.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

void pr_exit(int status)
{
    if (WIFEXITED(&status)) 
        printf("normal termination, exit status = %d\n",WEXITSTATUS(status));
    else if (WIFSIGNALED(&status))
            printf("abnormal termination,signal number = %d%s\n",WTERMSIG(status),
#ifdef  WCOREDUMP
                WCOREDUMP(status) ? " (core file generated)" : "");
#else
           "");
#endif
    else if(WIFSTOPPED(status))
        printf("child stoped signal number = %d\n",WSTOPSIG(status));
}

int main(void)
{
    pid_t    pid;
    int      status;

    if((pid = fork()) < 0){
        perror("forK");
    }
    if(pid == 0)
        exit(7);
    if(wait(&status) != pid){
        perror("wait");
    }
    pr_exit(status);
    if((pid = fork()) < 0){
        perror("fork");
    }
    if(pid == 0)
        abort();
    if(wait(&status) != pid){
        perror("wait1");
    }
    pr_exit(status);
    if(pid = fork()){
        perror("fork");
    }
    if(pid == 0){
        status /= 0;
    }
    if(wait(&status) != pid)
        perror("wait2");
    pr_exit(status);
    exit(0);
}




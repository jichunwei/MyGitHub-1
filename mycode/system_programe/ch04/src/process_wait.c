#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>
#include <sys/stat.h>

void out_status(int status)
{
    if(WIFEXITED(status)){
        printf("normal exit: %d\n", WEXITSTATUS(status));
    }
    else if(WIFSIGNALED(status)){
        printf("abnormal term: %d\n",
        WTERMSIG(status));
    }else if(WIFSTOPPED(status)){
        printf("stopped sig %d\n",
        WSTOPSIG(status));
    }
}

int main()
{
    int status;
    pid_t pid;
    if((pid = fork()) < 0)
        {
            perror("fork");
        }else if(pid == 0){
            printf("pid:%d,ppid:%d\n",getpid(),getppid());
            exit(3);
        }
    pid = wait(&status);
    printf("pid :%d ",pid);
    out_status(status);
    printf("------------------\n");
    if((pid = fork()) < 0)
    {
        perror("fork");
    }else if(pid == 0)
        {
            printf("pid :%d,ppid :%d\n",getpid(),getppid());
            int i = 3,j = 0;
            int k = i/j;
            printf("k is %d\n",k);
        }
            pid = waitpid(pid,&status,WUNTRACED);
            printf("pid :%d\n",pid);
            printf("----------------\n");
            if((pid = fork()) < 0){
                perror("fork");
            }
            else if(pid == 0)
            {
                printf("pid :%d,ppid %d\n ",getpid(),getppid());
            pause();
        }
    pid = wait(&status);
    printf("pid:%d ",pid);
    out_status(status);
    sleep(20);
    exit(0);

}




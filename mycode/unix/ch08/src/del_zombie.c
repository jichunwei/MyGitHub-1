#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <sys/wait.h>

int main()
{
    pid_t   pid;
    
    if((pid = fork()) < 0)
    {
        perror("fork");
        exit(1);
    }
    else if (pid == 0){
        if ((pid = fork()) < 0){
            perror("fork");
            exit(1);
        }
        else if (pid > 0)
            exit(0);
        sleep(2);
        printf("second child,parent pid = %d\n",getppid());
    }
    if(waitpid(pid,NULL,0) != pid){
        perror("waitpid");
    }
    exit(0);
}

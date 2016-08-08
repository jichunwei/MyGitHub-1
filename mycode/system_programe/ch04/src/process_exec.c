#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>

char *const cmd1 = "cat";
char *const cmd2 = "/bin/cat";
char *const argv1 = "/etc/passwd";
char *const argv2 = "/etc/group";

int main()
{
    pid_t pid;
    if((pid = fork()) < 0){
        perror("fork");
    }else if(pid == 0)
    {
        if(execl(cmd1,cmd1,argv1,argv2,NULL) < 0)
        {
            perror("excel");
            _exit(127);
        }else
            printf("execl %s success\n",cmd1);
    }
    wait(NULL);
    printf("------------\n");
    if((pid =fork()) < 0){
        perror("fork");
    }else if(pid == 0){
        if(execl(cmd2,cmd2,argv1,argv2,NULL) < 0)
        {
            perror("execl");
            _exit(127);
        }
        printf("execl %s success\n",cmd2);
    }
    wait(NULL);
    printf("------------\n");
    if((pid = fork()) < 0)
    {
        perror("fork");
    }
    else if(pid == 0){
         char *const argv[4] = {cmd1,argv1,argv2,NULL};
        if(execvp(cmd1,argv) < 0){
            perror("execvp");
            _exit(127);
        }
        printf("execvp %s success\n",cmd1);
    }
    wait(NULL);
    return 0;
}


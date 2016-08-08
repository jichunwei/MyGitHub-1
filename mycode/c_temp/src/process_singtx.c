#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#define     M   4

char *cmd1[3] = {"/bin/cat","/etc/passwd",NULL};
char *cmd2[3] = {"/bin/head","-10",NULL};
//char *cmd3[3] = {"/bin/grep","root",NULL};
//char *cmd4[3] = {"/bin/wc","-l",NULL};
int main()
{
    int fd[2];
    if(pipe(fd) < 0)
    {
        perror("pipe");
        exit(1);
    }
    int i = 1;
    pid_t pid;
    for(; i <=  M; i++)
    {
        pid = fork();
        if(pid < 0)
            perror("fork");
        else if(pid == 0)
        {
            if(1 == i){
                close(fd[0]);
                if(dup2(fd[1],STDOUT_FILENO) < 0){
                    perror("dup2");
                    exit(1);
                }
                close(fd[1]);
                if(execlp("/bin/bash","/bin/cat","/etc/passwd",NULL) < 0){
                    perror("execlp1");
                    exit(127);
                }
            }
            if(2 == i){
                close(fd[1]);
                if(dup2(fd[0],STDIN_FILENO) < 0){
                    perror("dup2");
                    exit(1);
                }
                close(fd[0]);
                if(execl("/bin/head","/bin/head","-10",NULL) < 0){
                    perror("execl2");
                    exit(127);
                }
            }
            if(3 == i){
                close(fd[0]);
                if(dup2(fd[1],STDOUT_FILENO) < 0){
                    perror("dup2");
                    exit(1);
                }
                close(fd[1]);
                if(execlp("/bin/grep","root",NULL) < 0){
                    perror("execlp3");
                    exit(127);
                }
            }
            if(4 == i){
                close(fd[1]);
                if(dup2(fd[0],STDIN_FILENO) < 0){
                    perror("dup2");
                    exit(1);
                }
                close(fd[0]);
                if(execlp("bin/wc","-l",NULL) < 0){
                    perror("execlp4");
                    exit(127);
                }
            }
        }
    }
    close(fd[0]);
    close(fd[1]);
    wait(NULL);
    wait(NULL);
    wait(NULL);
    wait(NULL);
    exit(0);
}


                
                
    
            




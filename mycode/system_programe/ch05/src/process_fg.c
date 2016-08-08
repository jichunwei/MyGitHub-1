#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

int fd;

void sig_handler(int signo)
{
    char *s1 = "SIGTTIN occured";
    char *s2 = "SIGTTOU occured";

    if(signo == SIGTTIN)
    {
        write(fd,s1,strlen(s1));
    }
    if(signo == SIGTTOU){
        write(fd,s2,strlen(s2));
    }
}

int main()
{
    fd = open("signal.txt",O_WRONLY|O_CREAT|O_TRUNC,S_IRWXU|S_IRWXG);
    if(fd <0)
    {
        perror("open");
    }
    if(signal(SIGTTIN,sig_handler) == SIG_ERR)
    {
        perror("signal");
        exit(1);
    }
    if(signal(SIGTTOU,sig_handler) == SIG_ERR)
    {
        perror("signal");
        exit(1);
    }
    if(setpgid(getpid(),getppid()) < 0)
    {
        perror("setpgid");
        exit(1);
    }
    pid_t pid;
    int i = 1;
    for(; i <= 2; i++)
    {
        pid = fork();
        if(pid < 0)
        {
            perror("fork");
        }
        else if(pid == 0)
        {//child process
            if(setpgid(getpid(),getpid()) < 0)
            {
                 perror("setpgid");
        }
            if(i == 1)
            {
                if(tcsetpgrp(0,getpgid(getpid())) < 0)
                    perror("tcsetpgrp");
            }
            break;
        }
        else {//parent process
            if(setpgid(pid,pid) < 0){
                perror("setpgid");
        }
            if(i == 1)
            {
                if(tcsetpgrp(0,getpgid(pid))< 0)
                    perror("tcsetpgrp");
            }
    }
   }
    char buff[2];
    if(3 == i)
    {
        read(0,buff,2);
    }
    if(2 == i)
    {
        char *p = "hello";
        write(1,p,strlen(p));
    }
    printf("pid:%d ppid:%d pgid :%d\n",getpid(),getppid(),getpgid(0));
    sleep(1);
    printf("waitingt for control signal\n");
    pause();
    exit(0);
}

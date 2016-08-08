#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/stat.h>

int g_v = 30;
int main()
{
    int a_v = 30;
    static int s_v = 30;
    FILE *fp = fopen("s.txt","w");
    int  fd = open("s_fd.txt",O_WRONLY|O_CREAT|O_TRUNC,S_IRWXU|S_IRWXG);
    char *s = "hello world";
    ssize_t size = strlen(s);
    fprintf(fp,"s:%s, g_v:%d ,a_v :%d; s_v: %d",s,g_v,a_v,s_v);
    write(fd ,s,size);
    pid_t pid;
    pid = fork();
    if(pid < 0)
    {//error
        perror("fork");
    }
    else if(pid > 0){//parent process
        g_v = 40;a_v = 40;s_v = 40;
    }
    else { //child process
        g_v = 50;a_v = 50; s_v = 50;
    }
    printf("g_v:%d,a_v:%d,s_v:%d\n",g_v,a_v,s_v);
    printf("pid:%d ppid:%d\n",getpid(),getppid());
    sleep(1);
    if(pid > 0) _exit(0);
    else
    exit(0);
}
            


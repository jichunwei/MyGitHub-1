#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <math.h>
#include "io.h"

void write_file(int fd,char *s)
{
    ssize_t size = strlen(s)*sizeof(char);
    ssize_t res;
    int i = 0;
    WRITE_LOCKW(fd,0,SEEK_SET,0);
    for(;i < size; i++)
    { 
         res = write(fd,s+1,1);
    if(res != 1){
        perror("write");
    }
    else{
        printf("%d write %d\n",getpid(),i);
    }
    usleep((int)(drand48()*10000));
    }
    UNLOCK(fd,0,SEEK_SET,0);
    sleep(1);

}

int main(int argc, char *argv[])
{
    int i =1;
    int fd;
    fd = open(argv[1],O_WRONLY|O_CREAT|O_TRUNC,S_IRWXU|S_IRWXG|S_IRWXO);
    if(fd < 0)
    {
        perror("open");
        exit(1);
    }
    pid_t pid;
    for(; i <= 3; i++)
    {
        pid = fork();
        if(pid == 0)break;
    }
    if(1 == i) write_file(fd,"11111111111");
    if(2 == i) write_file(fd,"22222222222");
    if(3 == i) write_file(fd,"33333333333");
    if(4 == i) write_file(fd,"44444444444");
    close(fd);
    return 0;
}


#include "io.h"
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

#define BUFFER_LEN  1024

void copy(int infd, int outfd)
{
    char buffer[BUFFER_LEN];
    ssize_t size;
    while((size = read(infd ,buffer, BUFFER_LEN)) > 0){
        if(write(outfd,buffer,size) != size){
        /*  char *s1 =strerror(errno);
            char *s2 = "write";
            char *s3 = "\n";
            write(2,s2,strlen(s2));
            write(2,s1,strlen(s1));
            write(2,s3,strlen(s3));
            */
            perror("write");
                    exit(1);
                    }
            }
            if(size < 0){
                perror("read");
            }
}

void set_f1(int fd,int flag)
{
    int v = fcntl(fd, F_GETFL);
    v |= flag;
    if(fcntl(fd, F_SETFL,v) < 0)
    {
        perror("fcntl");
    }
        
}

void clr_f1(int fd,int flag)
{
    int v = fcntl(fd ,F_GETFL);
    v &= ~flag;
    if(fcntl(fd, F_SETFL,v) < 0){
        perror("fcntl");
    }
}
int lock_reg(int fd, int cmd,int type, off_t offset,
        short whence,off_t length)
{
    struct flock flock;
    flock.l_type = type;
    flock.l_start = offset;
    flock.l_whence = whence;
    flock.l_len  = length;
    if(fcntl(fd, cmd,&flock) < 0){
        perror ("fcntl lock");
        return 0;
    }
//    printf("lock %d\n",flock.l_pid);
    return 1;
}

pid_t lock_test(int fd, short type,off_t offset,
        short whence,off_t length)
{
    struct flock flock;
    flock.l_type = type;
    flock.l_start = offset;
    flock.l_whence = whence;
    flock.l_len  = length;
   // flock.l_pid = pid;
    if(fcntl(fd, F_GETLK,&flock) < 0){
        perror ("fcntl lock");
        return -1;
    }
    return flock.l_pid;
}

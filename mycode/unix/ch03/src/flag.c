#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>

//设置文件状态标记
void set_fl(int fd,int flags)
{
    int     val;
    if((val = fcntl(fd,F_GETFL,0)) < 0){
        perror("fcntl");
        exit(1);
    }
    val |= flags;
    if(fcntl(fd, F_SETFL,val) < 0){
        perror("fcntl");
        exit(1);
    }
}

//去出文件状态标记
void clr_fl(int fd,int flags)
{
    int     val;
    if(val = fcntl(fd, F_GETFL ,0) < 0){
        perror("fcntl");
        exit(1);
    }
    val &= ~flags;
    if(fcntl(fd,F_SETFL,val) < 0){
        perror("fcntl");
        exit(1);
    }
}


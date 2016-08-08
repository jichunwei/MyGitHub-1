#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "flag.h"

int     fd;
int main(int argc,char *argv[])
{
    if(argc < 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    fd = open(argv[1],O_WRONLY,0777);
    if(fd < 0){
        perror("open");
        exit(1);
    }
  //  clr_fl(fd,O_WRONLY);
/*    ssize_t     size;
    char        buffer[1024];
    while((size = read(fd,buffer,1024)) > 0){
        if(write(STDOUT_FILENO,buffer,size) != size){
            perror("write");
            exit(1);
        }
        if(size < 0){
            perror("read");
            exit(1);
        }
    }
    */
    int val;
    if((val = fcntl(fd,F_GETFL)) < 0){
        perror("fcntl");
        exit(1);
    }
  //  set_fl(fd,O_CREAT);
    val |= O_CREAT|O_TRUNC;
    val &= ~O_TRUNC;
    fcntl(fd,F_SETFL,val);
    switch(val & O_ACCMODE){
        case O_WRONLY:
            printf("write only!\n");
            break;
        case O_RDONLY:
            printf("read only!\n");
            break;
        case O_RDWR:
            printf("read and write!\n");
            break;
        default:
            printf("error accmode!\n");
    }
    if(val & O_CREAT)
        printf("the file isn't exist!\n");
    if(val & O_TRUNC)
        printf("the file's size will be zero!\n");
    return 0;
}

#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc,char **argv)
{
    if(argc < 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    
    int     fd;
    if((fd = open(argv[1],O_RDWR)) < 0){
        perror("open");
        exit(1);
    }
    printf("fd:%d\n",fd);
    dup(fd);
    dup2(fd,4);
    close(fd);
    ssize_t     size;
    char        buffer[10];
    while((size = read(4,buffer,10)) > 0){
        if(write(1,buffer,size) != size){
            perror("write");
            exit(1);
        }
        if(size < 0){
            perror("read");
            exit(1);
        }
    }
    printf("\n");
    exit(0);
}


#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

int main(int argc,char **argv)
{
    if(argc != 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }

    int      fd;
    fd = open(argv[1],O_RDWR);
    if(fd < 0){
        perror("open");
        exit(1);
    }
    printf("fd:%d\n",fd);
    if(fcntl(fd,F_DUPFD,4) < 0){
        perror("fcntl");
        exit(1);
    }
    close(fd);
    printf("fd:%d\n",fd);
    ssize_t     size ;
    char        buffer[1];
    while((size = read(4,buffer,1)) > 0){
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

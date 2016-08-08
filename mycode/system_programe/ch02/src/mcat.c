#include <sys/types.h>
#include <stdio.h>
#include <errno.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

int main(int argc,char *argv[])
{
    if(argc < 2)
    {
        fprintf(stderr,"-usage:%s file\n",argv[0]);
       // printf("-usage:%s file\n",argv[0]);
        exit(1);
    }
    int infd;
    char buffer[1024];
    infd = open(argv[1],O_RDONLY);
    if(infd < 0){
        fprintf(stderr,"open:%s\n",strerror(errno));
        exit(1);
    }
    ssize_t size;
    while((size = read(infd,buffer,1024)) > 0){
        if(write(STDOUT_FILENO,buffer,size) != size){
            fprintf(stderr,"write:%s\n",strerror(errno));
        exit(1);
    }
    }
    if(size < 0){
        fprintf(stderr,"read:%s\n",strerror(errno));
    }
    close(infd);
    return 0;
}




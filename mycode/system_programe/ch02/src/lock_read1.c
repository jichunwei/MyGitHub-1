#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "io.h"

int main(int argc, char *argv[])
{
    if(argc < 2){
        fprintf(stderr,"-usage: %s file content\n",argv[0]);
        exit(1);
    }
    ssize_t size = strlen(argv[1]) * sizeof(char);
    int i = 0;
    int fd = open(argv[1],O_RDONLY,0777);
    if(fd < 0){
        perror("open");
        exit(1);
    }
    char *p = argv[1];
    READ_LOCK(fd,0,SEEK_SET,0);
  //  WRITE_LOCKW(fd,0,SEEK_SET,0);
    for(; i < size; i++)
    {
        if(read(fd ,(p+i), 1) !=1){
            perror("read");
        }
        printf("%d read %d \n",getpid(),i);
        int t = (int)(drand48() * 100000);
        usleep(t);
    }
    UNLOCK(fd,0,SEEK_SET,0);
    close(fd);
    printf("%d exit\n",getpid());
    return 0;
}

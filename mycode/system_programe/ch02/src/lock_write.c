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
    if(argc < 4){
        fprintf(stderr,"-usage: %s file content\n",argv[0]);
        exit(1);
    }
    ssize_t size = strlen(argv[2]) * sizeof(char);
    int i = 0;
    int fd = open(argv[1],O_WRONLY|O_CREAT,0777);
    if(fd < 0){
        perror("open");
        exit(1);
    }
    if((argv[3] != NULL) && !strcmp(argv[3],"lock")){
    if(!WRITE_LOCK(fd,0,SEEK_SET,0)){
        printf("lock pid: %d\n",
                lock_test(fd,F_WRLCK,0,SEEK_SET,0));
        exit(1);
    }
}
    char *p = argv[2];
    for(; i < size; i++)
    {
        if(write(fd ,(p+i), 1) !=1){
            perror("write");
        }
        printf("%d write %d \n",getpid(),i);
        int t = (int)(drand48() * 100000);
        usleep(t);
    }

    if((argv[3] != NULL) && (!strcmp("lock",argv[3]))){
    UNLOCK(fd,0,SEEK_SET,0);
    }
    close(fd);
    printf("%d exit\n",getpid());
    return 0;
}

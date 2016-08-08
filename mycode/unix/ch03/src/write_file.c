#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
/*
    *加O_APPEND使得lseek 无效
   */
int main(int argc ,char *argv[])
{
    int     fd;
    char    buf1[] = "abcdefgh";
    char    buf2[] = "12345678";

    if(argc != 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    if((fd = open(argv[1],O_WRONLY|O_CREAT|O_TRUNC|O_APPEND,0777)) < 0){
        perror("open");
        exit(1);
    }
    if(write(fd,buf1,sizeof(buf1)) != sizeof(buf1)){
        perror("write");
        exit(1);
    }
    if(lseek(fd,2,SEEK_SET) < 0){
        perror("lseek");
        exit(1);
    }
    if(write(fd,buf2,sizeof(buf2))  != sizeof(buf2)){
        perror("write");
        exit(1);
    }
    exit(0);
}
    

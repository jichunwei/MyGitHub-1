/*
   * lseek锁定文件处理位置
   */
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    int fd;

    if(argc != 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    
    if((fd = open(argv[1],O_RDONLY))< 0){
        perror("open");
        exit(1);
    }
    if(lseek(fd,0,SEEK_SET) < 0){
        perror("lseek");
        exit(1);
    }
    else 
        printf("seek success!\n");
    return 0;
}

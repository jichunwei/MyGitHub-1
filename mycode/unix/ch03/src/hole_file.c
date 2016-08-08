/*
  *产生空洞文件
   */
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

int main(int argc ,char *argv[])
{
    int     fd;
    char    buf1[] = "1234567";
    char    buf2[] = "abcdefg";

    if(argc != 2){
        fprintf(stderr,"-usage:%s\n",argv[0]);
        exit(1);
    }
    fd = open(argv[1],O_WRONLY|O_CREAT|O_TRUNC,0777);
    if(fd < 0){
        perror("open");
        exit(1);
    }
    if(write(fd,buf1,sizeof(buf1)) != sizeof(buf1)){
        perror("write");
        exit(1);
    }
    if(lseek(fd,1234,SEEK_SET) == -1){
        perror("lseek");
        exit(1);
    }
    if(write(fd,buf2,sizeof(buf2)) != sizeof(buf2)){
        perror("write");
        exit(1);
    }
    exit(0);
}
    

/*
    *pread和pwrite的用法
   */
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>


int main(int argc ,char *argv[])
{
    int     fd;
    ssize_t size;
    off_t   t;
    char    buf1[] = "12345678";
    char    buf2[] = "abcdefghijklm";
    
    if(argc != 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    fd = open(argv[1],O_RDWR|O_CREAT|O_TRUNC,0777);
    if(fd < 0){
        perror("oepn");
        exit(1);
    }
    if(write(fd,buf1,sizeof(buf1)) != sizeof(buf1)){
        perror("write");
        exit(1);
    }
    if((t = lseek(fd,5,SEEK_SET)) < 0){
        perror("lseek");
        exit(1);
    }
//    if((size = pread(fd,buf1,sizeof(buf1),t)) < 0){
 //       perror("pread");
  //      exit(1);
   // }
    if((pwrite(fd,buf2,sizeof(buf2),t)) != sizeof(buf2) ){
        perror("pwrite");
        exit(1);
    }
    exit(0);
}

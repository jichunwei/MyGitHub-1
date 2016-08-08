/*
   *对于给定的文件描述符打印文件状态标志
*/
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>

int main(int argc ,char *argv[])
{
    int     fd;
    int     val;

    if(argc < 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
//    fd = open(argv[1],O_WRONLY|O_CREAT|O_TRUNC,0777) ;
 //   if(fd < 0){
  //      perror("open");
   //     exit(1);
  //  }
    val = fcntl(atoi(argv[1]),F_GETFL,0);
    if(val < 0){
        perror("fcntl");
        exit(1);
    }
    switch(val & O_ACCMODE){
        case  O_RDONLY:
        printf("the file is readonly\n");
        break;
        case  O_WRONLY:
        printf("the file is writeonly\n");
        break;
        case O_CREAT:
        printf("tht file is not exits\n");
        break;
        default:
        printf("the file is dangerous!\n");
        if(val & O_APPEND)
            printf("the file can be append!\n");
        if(val & O_NONBLOCK)
            printf("the file is nonblock!\n");
    }
    return 0;
}

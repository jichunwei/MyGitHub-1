#include "io.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

#define LEN 1024


void copy(int infd ,int outfd)
{
    char buff[LEN];
    ssize_t size;
    while((size =read (infd, buff,LEN)) > 0){
        if(write(outfd ,buff,size) != 0)
        {
            perror("write");
            exit(1);
        }
    }
        if(size < 0)
            perror("read");
}
            
int main(int argc,char *argv[])
{
/*   // int infd = STDIN_FILENO;
    int infd = 0;
    //int outfd = STDOUT_FILENO; 
    int outfd = 1;
    int i;
    for(i = 1; i < argc; i++){
        infd = open(argv[i],O_WRONLY|O_CREAT|O_TRUNC);
        if( infd < 0)
        perror("open");
            continue;
    }
    copy(infd ,outfd);
    close(infd);
    */
    if(argc == 1)
         printf("usage:%s file1 file2\n",argv[0]);
    if(argc == 2)
        printf("usage:%s missing  destination file\n",argv[0],argv[1]);
    if(argc == 3){
        copy(argv[1],argv[2]);
     /*   int ifnd = 0;
        int outnd = 1;

        char buff[LEN];
        ssize_t size ;
        while((size = read (argv[1],buff,LEN)) > 0){
            if(write(argv[2],buff,size) != size)
            {
                perror("writer");
                exit(1);
            }
        }
        if(size < 0){
            perror("read");
            exit(1);
        }
    }
    */
    return 0;
}
}


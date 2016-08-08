#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include "io.h"

int main(int argc , char *argv[])
{
    if(argc < 5 ){
        fprintf(stderr,"-usage:%s + inf - outf\n",argv[0]);
        exit(1);
    }
    int i = 1 ;
    for(; i < 5; i++)
    {
        if(!strcmp( "+",argv[i])){
            int fd = open(argv[i+1],O_RDONLY);
            if(fd , 0){
                perror("open");
                exit(1);
            }
            if(dup2(fd,STDIN_FILENO) != STDIN_FILENO){
                perror("dup2");
                exit(1);
            }
            close(fd);
            i++;
        }
        if(!strcmp("-",argv[i])){
            int fd = open(argv[i + 1],O_WRONLY|O_CREAT|O_TRUNC,0777);
            if(fd < 0){
                perror("open");
                exit(1);
            }
            if(dup2 (fd,STDOUT_FILENO) != STDOUT_FILENO){
                perror("dup2");
                exit(1);
            }
            close(fd);
            i++;
        }

    }
    copy(STDIN_FILENO,STDOUT_FILENO);
    return 0;
}



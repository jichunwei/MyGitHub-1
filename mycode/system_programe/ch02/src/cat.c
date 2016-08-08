#include "io.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(int argc,char *argv[])
{
   // int infd = STDIN_FILENO;
    int infd = 0;
    //int outfd = STDOUT_FILENO; 
    int outfd = 1;
    int i;
    for(i = 1; i < argc; i++){
        infd = open(argv[i],O_RDONLY);
        if(infd < 0){
            perror("open");
            continue;
    }
    copy(infd ,outfd);
    close(infd);
    }
    if(argc == 1)copy(infd,outfd);
    return 0;
}


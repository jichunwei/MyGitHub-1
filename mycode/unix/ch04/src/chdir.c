#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

int main(int argc ,char *argv[])
{
    int     path;
    
    if(argc != 2){
        fprintf(stderr,"usage:%s pathname\n",argv[1]);
        exit(1);
    }
    if((path = chdir("/home/tan/unix/ch04/bin")) < 0){
        perror("chmdir");
    }else {
        printf("chdir success!\n");
        if(fchdir(atoi(argv[1])) < 0){
            perror("fchdir");
            exit(1);
        }
    }
    exit(0);
}

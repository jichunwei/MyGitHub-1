#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc ,char *argv[])
{
    if(argc < 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    if(access(argv[1],R_OK) < 0){
        perror("access");
    }else 
        printf("read access ok!\n");
    if(open(argv[1],O_RDONLY) < 0){
        perror("open");
        exit(1);
    }
    else 
        printf("open for reading ok!\n");
    exit(0);
}

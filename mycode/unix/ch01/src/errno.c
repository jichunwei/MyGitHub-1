#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc,char *argv[])
{
    if(argc != 2) {
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    fprintf(stderr,"EACCES:%s\n",strerror(EACCES));

    errno = ENOENT;
    perror("errno");
    exit(1);
}

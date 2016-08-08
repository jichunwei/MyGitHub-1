#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>

static pfd1[2],pfd2[2];

void tell_wait()
{
    if((pipe(pfd1) < 0) || (pipe(pfd2) < 0)){
        perror("pipe");
        exit(1);
    }
}

void wait_parent()
{
    char    c;

    if(read(pfd1[0],&c ,1) != 1){
        perror("write");
    }
    if(c != 'p')
        printf("wait_parent:incorrect data\n");
}

void tell_paretn()
{
    if(write(pfd2[1],"c",1) != 1){
        perror("write");
        exit(1);
    }
}

void wait_child()
{
    char c;

    if(read(pfd2[0],&c,1) != 1){
        perror("read");
        exit(1);
    }
    if(c != 'c')
        printf("wiat_child: incorrect data\n");
}

void tell_child()
{
    if(write(pfd1[2],"c",1) != 1){
        perror("write");
        exit(1);
    }
}


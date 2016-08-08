#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

static void exit1()
{
    printf("frist exit handler!\n");
}

static void exit2()
{
    printf("second exit hanler!\n");
}

int main()
{
    if(atexit(exit1) < 0){
        perror("atexit");
    }
    if(atexit(exit1) < 0){
        perror("atexit");
    }
    if(atexit(exit2) < 0){
        perror("atexit");
        exit(1);
    }
    printf("main is done!\n");
    exit(0);
}



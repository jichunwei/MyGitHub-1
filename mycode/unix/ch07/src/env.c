#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

int main(int argc,char *argv[])
{
    int     i;

    if(argc < 2){
        fprintf(stderr,"-usage:%s\n",argv[0]);
        exit(1);
    }
    for(i = 1; i < argc; i++)
    {
    if(getenv(argv[i]) == NULL){
        perror("getenv");
        continue;
        }
    if(putenv("PWD=/home") < 0){
        perror("putenv");
        break;
    }
    if(setenv("/home","PWD",1) < 0){
        perror("setenv");
        break;
    }
    }
    exit(0);
}

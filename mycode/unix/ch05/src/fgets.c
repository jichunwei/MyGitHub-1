#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#define     BUFSIZE     1024

int main()
{
    char    buff[BUFSIZE];

    while(fgets(buff,BUFSIZE,stdin) > 0){
        if(fputs(buff,stdout) < 0){
            perror("fputs");
        }
        if(ferror(stdin)){
            perror("fgets");
            exit(1);
        }
    }
    return 0;
}

#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int main()
{
    char    ch;
     
    while((ch = getc(stdin)) != EOF){
 //       sleep(2);
 //       exit(0);
        if(putc(ch,stdout) == EOF){
            perror("putc");
            exit(1);
        }
    }
    if(ch == EOF){
        perror("getc");
        exit(1);
    }
    exit(0);
}

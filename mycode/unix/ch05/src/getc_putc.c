#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    int     c;
    
    while(( c = getc(stdin)) > 0){
        if(putc(c,stdout) < 0){
            perror("putc");
        }
        if(ferror(stdin)){
            perror("getc");
            exit(1);
        }
    }
    return 0;
}


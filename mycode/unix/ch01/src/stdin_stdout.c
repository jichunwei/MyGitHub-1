#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#define  MAXSIZE    1024

int main()
{
    ssize_t     size;
    char        buffer[MAXSIZE];

    while((size = read(STDIN_FILENO,buffer,MAXSIZE)) > 0){
        if(write(STDOUT_FILENO,buffer,size) != size){
            perror("write");
            exit(1);
        }
    }
    if(size < 0){
        perror("read");
    }
    exit(0);
}

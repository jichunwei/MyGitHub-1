#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    int     fd;
    char    buffer[1024] = "tang";

    if((fd = open("bar",O_RDWR)) < 0){
        perror("open");
    }
    if(lseek(fd,1234,SEEK_SET) < 0){
        perror("lseek");
    }
    if(write(fd,buffer,1024) != 1024){
        perror("write");
        exit(1);
    } 
}

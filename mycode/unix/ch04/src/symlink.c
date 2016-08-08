#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>

int main()
{
    ssize_t     size;
    char        buffer[1024];

    if(symlink("xh","tsx") < 0){
        perror("symlink");
    }
    size = readlink("tsx",buffer,1024);
    if(size < 0){
        perror("size");
        exit(1);
    }
    exit(0);
}

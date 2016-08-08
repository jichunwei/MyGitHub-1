#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include "io.h"
#include <stdlib.h>
#include <fcntl.h>

int main()
{
    char buffer[250000];
    ssize_t size;
    if((size = read (STDIN_FILENO,buffer,250000)) < 0)
    {
        perror("read");
        exit(1);
    }
    ssize_t total_size = 0,curr_size = 0;
    char *p = buffer;
    set_f1(STDOUT_FILENO,O_NONBLOCK);
    while((curr_size = write(STDOUT_FILENO,p,
                    (size-total_size))) != (size - total_size)){
        if(curr_size < 0){
            perror("write");
        }else
        {
            total_size += curr_size;
        p += curr_size;
        fprintf(stderr,"write success: %d,%d\n",curr_size,total_size);
        }
    }
    return 0;

}

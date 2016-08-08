#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <error.h>
#include <string.h>
#include "io.h"

int main()
{
    char buffer[4096];
    ssize_t size = 0;
    set_f1(STDIN_FILENO,O_NONBLOCK);
    while((size = read(STDIN_FILENO,buffer,4086)) != 0)
    {
        if(size > 0)
        {
            if(write(STDOUT_FILENO,buffer,size) != size)
            {
                perror("write");
            }
        }
        else
        {
            perror("nonread");
        }
        sleep(5);
    }
    return 0;
}

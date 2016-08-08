#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    int i,j;
    if(read(STDIN_FILENO,&i,sizeof(int)) < 0)
    {
        perror("read");
    }
    if(read(STDIN_FILENO,&j,sizeof(int)) < 0)
    {
        perror("read");
    }
    int  k = 0,a = i;
    for(; a <= j; i++)
    {
        k += a;
    }
    if(write(STDOUT_FILENO,&k,sizeof(int)) != sizeof(int))
    {
        perror("write");
    }
    exit(0);
}



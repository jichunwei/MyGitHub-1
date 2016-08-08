#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>

int main()
{
    printf("hello tan process id!(%d)\n",getpid());
    return 0;
}

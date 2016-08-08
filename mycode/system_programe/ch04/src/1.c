#include <sys/resource.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
    struct rlimit limit;
    if(getrlimit(RLIMIT_NOFILE,&limit) < 0)
    {
        perror("getrlimit");
        exit(1);
    }
    limit.rlim_cur = 4;
    if(setrlimit(RLIMIT_NOFILE,&limit) < 0)
    {
        perror("setrlimit");
        exit(1);
    }
    if(open("a1",O_WRONLY|O_CREAT|O_TRUNC,0777) < 0)
    {
        perror("creat a1");
    }
    if(open("a2",O_WRONLY|O_CREAT|O_TRUNC,0777)<0)
        perror("creat a2");
    if(open("a3",O_WRONLY|O_CREAT|O_TRUNC,0777)< 0)
        perror("creat a3");
    return 0;
}

            
    


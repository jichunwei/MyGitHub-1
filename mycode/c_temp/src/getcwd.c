#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int  main()
{
    char *ptr;
    size_t size;

    if(chdir("/home/tan/system") < 0)
        perror("chdir failer");

//    ptr = path_alloc(&size);
    ptr = (char *)malloc(sizeof(char));
    if(getcwd(ptr,size) == NULL)
        perror("getcwd failer");

    printf("cwd = %s\n",ptr);
    exit(0);
}

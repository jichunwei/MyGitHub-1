#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>

int main(int argc,char **argv)
{
    int     i;
    char    **ptr;
    char    **environ;

    if(argc < 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }
    for(i = 0; i < argc; i++)
    {
        printf("argv[%d]:%s\n",i,argv[i]);
    }
    for(ptr = environ; *ptr != 0; ptr++)
        printf("%s\n",*ptr);

    exit(0);
}

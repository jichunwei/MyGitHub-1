#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>

int main()
{
    char *file = "/etc/shadow";
    FILE *fp  =  fopen(file ,"r");
    if(fp == NULL)
    {
        fprintf(stderr,"fopen:%s(%d)\n",strerror(errno),errno);
        perror("fopen:");
        exit(1);
    }
    printf("open file %s success\n",file);
    return 0;

}

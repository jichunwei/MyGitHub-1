#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <dirent.h>

int main(int argc,char *argv[])
{
    DIR         *dp;
    struct dirent *dirp;
    
    dp = opendir(argv[1]);
    if(dp == NULL){
        perror("opendir");
        exit(1);
    }
    while((dirp = readdir(dp)) != NULL){
        printf("%s\n",dirp->d_name);
    }
    closedir(dp);
    exit(0);
}

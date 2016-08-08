#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(int argc, char *argv[])
{
    int     i;
    struct  stat stat;

    for(i = 1; i < argc ; i++)
    {
        printf("%s \n",argv[i]);
       if(lstat(argv[i],&stat) < 0){
           perror("lseek");
           continue;
       }
       if(S_ISREG(stat.st_mode))
           printf("normal file\n");
       else if(S_ISCHR(stat.st_mode))
           printf("character file!\n");
       else if(S_ISDIR(stat.st_mode))
           printf("dirent file!\n");
       else if(S_ISBLK(stat.st_mode))
           printf("block file!\n");
       else if(S_ISFIFO(stat.st_mode))
           printf("fifo file!\n");
       else if(S_ISLNK(stat.st_mode))
           printf("link file!\n");
       else if(S_ISSOCK(stat.st_mode))
           printf("sock file!\n");
       else
           printf("** unkown mode **\n");
       printf("*******\n");
    }
    return 0;
}

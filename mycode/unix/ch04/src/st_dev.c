#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc,char *argv[])
{
    int             i;
    struct  stat statbuf;

    for(i = 1; i < argc; i++)
    {
        printf("%s :\n",argv[i]);
        if(lstat(argv[i],&statbuf) < 0){
            perror("lstat");
            continue;
        }
        printf("dev = %d/%d",major(statbuf.st_dev),minor(statbuf.st_dev));
        if(S_ISCHR(statbuf.st_mode) || S_ISBLK(statbuf.st_mode)){
            printf("(%s) rdev = %d/%d",S_ISCHR(statbuf.st_mode)?"character":"block",
                        major(statbuf.st_rdev),minor(statbuf.st_rdev));
        }
        printf("\n");
    }
    exit(0);
}

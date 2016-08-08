#include <unistd.h>
#include <errno.h>
#include <utime.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <stdio.h>

int main(int argc,char *argv[])
{
    int             i,fd;
    struct stat      statbuf;
    struct utimbuf  timebuf;

    for(i = 1; i < argc; i++){
        if(stat(argv[i],&statbuf) < 0){
            perror("lstat");
            continue;
        }
        if((fd = open(argv[i],O_RDWR|O_TRUNC)) < 0){
            perror("open");
            continue;
        }
        close(fd);
        timebuf.actime = statbuf.st_atime;
        timebuf.modtime = statbuf.st_mtime;
        if(utime(argv[i],&timebuf) < 0){
            perror("utime");
            continue;
        }
    }
    exit(0);
}

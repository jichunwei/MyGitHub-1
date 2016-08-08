#include <unistd.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>

#define     RWRWRW  S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH|S_IWOTH

int main()
{
    umask(0);
    if(creat("foo",RWRWRW) < 0){
        perror("open");
    }
    umask(S_IRGRP|S_IWGRP|S_IROTH|S_IWOTH);
    if(creat("bar",RWRWRW) < 0){
        perror("open1");
    }
    if(chmod("bar",S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH) < 0){
        perror("chmod");
        exit(1);
    }
    exit(0);
}

#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc,char *argv[])
{
    int fd1 = atoi(argv[1]);
    int fd2 = atoi(argv[2]);
    printf("fd1 exec:%d\n",fcntl(fd1,F_GETFD));
    printf("fd2 exec:%d\n",fcntl(fd2,F_GETFD));
    char *s = "hello,exec";
    ssize_t size = strlen(s)*sizeof(char);
    if(write(fd1,s,size) != size){
        perror("write fd1");
    }
    if(write(fd2,s,size) != size){
        perror("write fd2");
    }
    close (fd1);
    close(fd2);
    return 0;
}



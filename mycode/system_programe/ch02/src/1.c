#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

int main(int argc ,char *argv[])
{
    if(argc < 2){
        fprintf(stderr,"-usage:%s[file]\n",argv[0]);
        exit(1);
    }
    int fd = open(argv[1],O_WRONLY|O_CREAT,0777);
    if(fd < 0)
    {
        perror("open");
        exit(1);
    }
    printf("file length: %ld\n",lseek(fd,0,SEEK_END));
    char *buffer = "0123456789";
    size_t size = strlen(buffer);
    sizeof(char);
    if(write(fd,buffer,size) != size){
        perror("write");
        exit(1);
    }

    printf("file length: %ld\n",lseek(fd,0,SEEK_END));
    if(lseek(fd,10,SEEK_END) < 0){
        perror("lseek");
        exit(1);
    }

    printf("file length: %ld\n",lseek(fd,0,SEEK_END));
    close(fd);
    return 0;
}


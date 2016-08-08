#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int main( int argc, char *argv[])
{
    if(argc < 2 )
    {
        fprintf(stderr,"-usage:%s file\n",argv[0]);
        exit(1);
    }
    int fd = open(argv[1],O_RDWR);
    if(fd < 0)
    {
        perror("open");
        exit(1);
    }
    char *addr;
    addr = mmap(0,20,PROT_WRITE,MAP_SHARED,fd,0);
    if(addr < 0){
        perror("mmap");
        exit(1);
    }
    int i = 0;
    for(; i <= 20; i++){
        *(addr + i) = 'A' + i;
    }
    printf("modify finished\n");

    sleep(30);
    munmap(addr,0);
    close(fd);
    return 0;
}

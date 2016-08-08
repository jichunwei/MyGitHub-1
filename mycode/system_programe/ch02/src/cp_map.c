#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <errno.h>
#include <sys/mman.h>
#include <memory.h>

int main(int argc, char *argv[])
{
    if(argc < 3)
    {
        fprintf(stderr, "-usage: %s f1 f2\n",argv[0]);
        exit(1);
    }
    int std = open(argv[1],O_RDONLY);
    if(std < 0){
        perror("open");
        exit(1);
    }
    int dfd = open(argv[2],O_RDWR|O_CREAT|O_TRUNC,0777);
    if(dfd < 0){
        perror("open");
        exit(1);
    }
    off_t len = lseek(std, 0,SEEK_END);
    if(lseek(dfd,len-1,SEEK_SET) < 0)
    {
        perror("lseek");
        exit(1);
    }
    if(write(dfd,"0",1) != 1){
        perror("write");
        exit(1);
    }
        char *addr = mmap(0,len,PROT_READ,MAP_PRIVATE,std,0);
    if(addr < 0 ){
        perror("mmap");
        exit(1);
    }
        char  *addr1 = mmap(0,len,PROT_WRITE, MAP_SHARED,dfd,0);
        if(addr1 < 0){
            perror("mmap");
            exit(1);
        }
    memcpy(addr1,addr,len);
    munmap(addr, 0);
    munmap(addr1,0);
    close(std);
    close(dfd);
    return 0;
}    
    

            
            

            


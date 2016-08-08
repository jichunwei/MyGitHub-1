#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc,char *argv[])
{
    if(argc < 2)
    {
        fprintf(stderr,"-usage:%s file content\n",argv[0]);
        exit(1);
    }
    int fd = open(argv[1], O_WRONLY|O_CREAT|O_APPEND,0777);
    if(fd < 0){
        perror("open");
        exit(1);
    }
   // set_f1(fd,O_APPEND);
    size_t size =strlen(argv[2]) * sizeof(char);
    if(lseek(fd,0,SEEK_SET) < 0){
        perror("lseek");
        exit(1);
    }
    sleep(5);
    if(write(fd,argv[2],size)  != size){
        perror("lseek");
        exit(1);
    }
    close(fd);
    printf("%d exit\n",getpid());
    return 0;
}
    


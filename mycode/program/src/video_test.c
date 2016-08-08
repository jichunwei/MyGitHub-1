#include "video.h"
#include <fcntl.h>
#include "print.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc,char *argv[])
{
    int     cameraFd;

    if(argc != 2){
        fprintf(stderr,"-usage:%s devname\n",argv[0]);
        exit(1);
    }
    printf("***program begin***\n");
    get_dev(argv[1]);
    printf("devname:%s\n",argv[1]);
  //  open_dev(argv[1],cameraFd);
    if((cameraFd = open(argv[1],O_RDWR)) < 0){
        perror("open");
        exit(1);
    }
    printf("cameraFd:%d\n",cameraFd);
    get_capability(cameraFd);
    select_input(cameraFd);
    get_standard(cameraFd);
    set_frame(cameraFd);
    do_frame(cameraFd);

}

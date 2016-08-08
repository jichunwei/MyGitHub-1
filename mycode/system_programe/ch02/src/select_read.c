#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
    struct timeval t;
    t.tv_sec = 4;
    t.tv_usec = 0;
    fd_set readset;
    FD_ZERO(&readset);
    FD_SET(STDIN_FILENO,&readset);
   // FD_SET(fd1,&readset);
    //FD_SET(fd2,&readset);
    int counter;
    while((counter = select(STDIN_FILENO + 1,
                    &readset,NULL,NULL,&t)) >= 0){
        if(counter == 0)
        {
            printf("select timeout\n");
        }
        else{
            if(FD_ISSET(STDIN_FILENO,&readset)){
                char buffer[1024];
                ssize_t size;
                size = read(STDIN_FILENO,buffer,1024);
                write(STDOUT_FILENO,buffer,size);
            }
            /*
               if(FD_ISSET(fd2,&readset)){}
               if(FD_ISSET(fd3,&readset)){}
               */
        }
            FD_ZERO(&readset);
            FD_SET(STDIN_FILENO,&readset);
        t.tv_sec = 4;
        t.tv_usec = 0;
    }
    return 0;
}
               

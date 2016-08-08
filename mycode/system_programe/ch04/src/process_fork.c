#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    int i = 1;
    pid_t p1;
    p1 = fork();
    if(p1 < 0)
    {//error
        perror("p1:fork");
    }
    else if(p1 == 0) {
        //child process
        i = 2;
        pid_t p2;
        p2 = fork();
        if(p2 < 0) {
            //error
            perror("p2:fork");
        }else if(p2 == 0)//child process(p2)
            i = 3 ;
 /*       pid_t p3;
        p3 = fork();
        if(p3 < 0){
            //error
            perror("p3: fork");
        }
        else if(p3 == 0)
            i = 4;
       pid_t p4;
        p4 = fork();
        if(p4 < 0)
        {
            perror("p4:fork");
        }
        else if(p4 == 0)
            i = 5;
        
    }
    */
}
    printf("i: %d,pid %d,ppid:%d\n",i,getpid(),getppid());
    sleep(10);
    exit(0);
}


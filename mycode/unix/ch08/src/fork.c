#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int a = 1;
int main(void)
{
    int      b = 2;
    pid_t    pid;
    char buffer[] = "a write to stdout\n";

    if(write(STDOUT_FILENO,buffer,strlen(buffer)) != strlen(buffer)){
        perror("write");
        exit(1);
    }
    printf("before fork\n");
    if(pid = fork() < 0){
        perror("fork");
        exit(1);
    }if(pid == 0){
        a++;
        b++;
    }else{
        sleep(2);
    }
    printf("pid:%d a:%d b:%d\n",getpid(),a,b);
    return 0;
}

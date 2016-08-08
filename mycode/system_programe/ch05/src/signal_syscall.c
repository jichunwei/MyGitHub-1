#include <signal.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void sig_handler(int signo)
{
    if(signo == SIGTSTP)
    {
        printf("SIGTSTP occured\n");
    }
}

int main()
{
    char buffer[512];
    ssize_t size;
    if(signal(SIGTSTP,sig_handler) == SIG_ERR)
    {
        perror("signal");
    }
    printf("begin running an waiting for signal\n");
    size = read( STDIN_FILENO,buffer,512);
    if(size < 0)
    {
        perror("read");
    }
    printf("reading finished\n");
    if(write(STDOUT_FILENO,buffer,size) != size){
        perror("write");
    }
printf("end running\n");
exit (0);
}

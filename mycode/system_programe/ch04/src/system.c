#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>

char *cmd1 = "date >s1.txt";
char *cmd2 = "date >s2.txt";
 
void msystem(char *cmd)
{
    pid_t pid;
    if((pid = fork()) < 0)
    {
        perror("fork");
    }
    else if(pid == 0)
    {
        if(execlp("/bin/bash","/bin/bash","-c",cmd,NULL) < 0){
            perror("execlp");
        }
    }
    else {
        wait(NULL);
    }
}
int main()
{
    system(cmd2);
    msystem(cmd1);
    return 0;
}

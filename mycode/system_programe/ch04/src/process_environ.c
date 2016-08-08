#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern char ** environ;

int main()
{
    int i = 0;
    char *env;
    while((env = environ[i]) != NULL){
        printf("%s\n",env);
        i++;
    }
    return 0;
}

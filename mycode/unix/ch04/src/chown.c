#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>

int main()
{
    if(chown("foo",0,0) <0){
        perror("chown");
        exit(1);
    }
    exit(0);
}

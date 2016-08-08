#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>

int main()
{
    if(link("bar","bar2") < 0){
        perror("link");
        exit(1);
    }
    sleep(3);
    if(unlink("bar1") < 0){
        perror("unlink");
        exit(1);
    }
    exit(0);
}

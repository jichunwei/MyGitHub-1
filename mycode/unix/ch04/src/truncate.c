#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>

int main()
{
    if(truncate("bar",100) < 0){
        perror("truncate");
        exit(1);
    }
    exit(0);
}

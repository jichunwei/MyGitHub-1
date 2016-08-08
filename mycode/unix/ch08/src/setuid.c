#include <unistd.h>
#include <stdio.h>

int main()
{
    setreuid(0,6035);
    setregid(-1,6035);
    printf("%d %d\n",getuid(),geteuid());
    printf("%d %d\n",getgid(),getegid());
    return 0;
}

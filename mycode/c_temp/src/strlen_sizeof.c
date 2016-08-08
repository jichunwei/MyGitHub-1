#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

int main()
{
    char a[6]= "tan";
    
    printf("%d\n",strlen(a));
    printf("%d\n",sizeof(a));
    return 0;
}

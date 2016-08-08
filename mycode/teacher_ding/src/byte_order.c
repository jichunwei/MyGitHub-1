#include<stdio.h>

int byte()
{

    unsigned short d = 0x1122;
    char *p = (char *)&d;
    if(*p == 0x22)
    {
	return 0;
    }
    return 1;
}
 
int main()
{
    printf("%s\n",(byte()?"big-endian":"litter-endian"));
    return 0;
}



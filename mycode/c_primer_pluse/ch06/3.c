#include<stdio.h>
int main()
{
    int i;
    i=3;
    while(i)
        printf("%d is true\n",i--);
    printf("%d is false\n",i);
    return 0;
}

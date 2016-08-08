#include<stdio.h>
int main()
{
    int i,j;
    for(i=0,j=10;i<j;i+=2,j--)
        printf("i=%d\n",i);
    printf("j=%d\n",j);
}

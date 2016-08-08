#include<stdio.h>
int main()
{
    int f1=1,f2=1;
    int i;
    for(i=1;i<=20;i++)
    {
        f1=f1+f2;
        f2=f1+f2;
        printf("NO.%d,%d\n",i,f2+f1);
    }
    printf("\n");
}

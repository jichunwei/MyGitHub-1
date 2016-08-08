#include<stdio.h>
int main()
{
    int i ,f1=1;
    for(i=2;i<=10;i++)
        f1=2*(f1+1);
    printf("%4d\n",f1);
}

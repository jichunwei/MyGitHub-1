#include<stdio.h>
int main()
{
    int a=0,n,b;
    int k;
    printf("input a num:");
    scanf("%d",&n);
    for(b=0;b<4;b++)
    {
    a=a*10+n%10;
   n=n/10;
    }
    printf("%d\n",a);
}

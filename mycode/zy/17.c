#include<stdio.h>
int main()
{
    float s;
    int n,i;
    printf("enter a num:");
    scanf("%d",&n);
    for(i=1;i<=n;i++)
    {s=(s+n/2)/2;
    i++;}
    printf("%f\n",s);
}


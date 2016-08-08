#include<stdio.h>
int main()
{
   long int i,a,b;
    printf("input a num:");
    scanf("%d",&a);
   b=a;
    for(i=1;i<=5;i++)
    {
       a+=a*10+b;
      printf("a=%10d\n",a);
    }
}

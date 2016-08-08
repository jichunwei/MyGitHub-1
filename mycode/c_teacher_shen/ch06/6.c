#include<stdio.h>
int main()
{
    int f(int n);
    int n,i;
    printf("input a num:");
    scanf("%d",&n);
   i=f(n);
   printf("i!=%d\n",i);
    
   return 0;
}
int f(int n)
{
   int i;
   int k=1;
   for(i=1;i<=n;i++)
   k*=i;
   return k;
}

#include<stdio.h>
#define SIZE 4
int main()
{
     int a[SIZE]={13,543};
     int i;
     printf("%2s %14s\n","i","a[i]");
     for(i=0;i<SIZE;i++)
     {
         printf("%2d%14d\n",i,a[i]);
     }
     return 0;
}


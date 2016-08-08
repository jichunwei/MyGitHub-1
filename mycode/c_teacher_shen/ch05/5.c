#include<stdio.h>
int main()
{
   int a[10]={1,3,4,4,5,3,3,5,6,7};
   int *p,i;
   for(i=0;i<10;i++)
       printf("a[%d]=%d\n",i,a[i]);
   for(p=&a[0];p<(p+10);p++)
       printf("p=%d\n",*p);
   return 0;
}

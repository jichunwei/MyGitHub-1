#include<stdio.h>
int main()
{
    int *p1,*p2,*p,a,b;
    printf("enter two num:");
    scanf("%d,%d",&a,&b);
  //  p1=&a;p2=&b;
    if(a<b)
    {p1=&b;p2=&a;}
  //  {p=p1;p1=p2;p2=p;}
    printf("%d %d\n",a,b);
    printf("%d %d\n",*p1,*p2);
    return 0;
}

#include<stdio.h>
int main()
{
    int max(int a,int b);
    int min(int a,int b);
    int sum(int a,int b); 
    void fun(int,int ,int (*p)(int a,int b));
    int a =43,b=33,c;
    int d;
    printf("input 1|2|3:");
    scanf("%d",&c);
    if(c==1) fun(a,b,max);
  /*  {
        p=max;
        d=max(a,b);
        printf("max=%d\n",d);
    }
    */
    else if(c==2) fun(a,b,min);
   /* {
        p=min;
        d=min(a,b);
        printf("min=%d\n",d);
    }
    */

    else if (c==3) fun(a,b,sum);
   /* {
        p=sum;
        d=sum(a,b);
        printf("sum=%d\n",d);
    }
    */
    return 0;
}
int max(int a,int b)
{
  printf("max= ");  return(a>b?a:b);
}
int min(int a,int b)
{
  printf("min=");  return(a<b?a:b);
}
int sum(int a,int b)
{
  printf("sum=");  return (a+b);
}
void fun(int a,int b,int(*p)(int a,int b))
{
  int result;
  result=(*p)(a,b);
  printf("%d\n",result);
}
       

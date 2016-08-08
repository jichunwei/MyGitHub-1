#include<stdio.h>
int main()
{
    int a,b,t,k;
    printf("enter two num:");
    scanf("%d %d",&a,&b);
    t=f(a,b);
    k=f1(a,b);
    printf("%3d\n%3d\n",t,k);
    printf("\n");
    return 0;
}
int f(int a, int b)
{   
    int t;
    if(a>b)
    {t=a%b;a=b;b=t;}
    return t;
    if(a>b)
    {t=a;a=b;b=a;
    t=a%b;a=b;b=t;}
    return t;
}
int f1(int a,int b)
{
  return(a*b/f(a,b));
} 
    

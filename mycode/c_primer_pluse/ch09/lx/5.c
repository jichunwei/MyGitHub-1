#include<stdio.h>
int main()
{
    int lager_of(int *,int *);
    int a,b;
    printf("Please input two nums:");
    scanf("%d%d",&a,&b);
    lager_of(&a,&b);
    printf("%3d %3d\n",a,b);
    return 0;
}
int lager_of(int *x,int *y)
{
    int t;
    if(*x>*y)
    { t=*x;*y=t;}
    else
    {t=*y;*x=t;}
    return t;
}
    
    

#include<stdio.h>
int main()
{
    int imax(int ,int );
    int a,b;
    a=2,b=3;
    printf("%d %d %d\n",a,b,imax(a,b));
    return 0;
}
int imax(int a,int b)
{
    return (a>b?a:b);
}

    


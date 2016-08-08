#include<stdio.h>
int main()
{
    int max4(int a,int b,int c,int d);
    int max2(int ,int );
    int a,b,c,d,max;
    printf("enter 4 num:");
    scanf("%d %d %d %d",&a,&b,&c,&d);
    max=max4(a,b,c,d);
    printf("%d\n",max);
    return 0;
}
int max4(int a,int b,int c,int d)
{
    int m;
    m=max2(a,b);
    m=max2(m,c);
    m=max2(m,d);
    return m;
}

int max2(int a,int b)
{
    int i;
    i=(a>b)?a:b;
    return i;
}



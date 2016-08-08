#include<stdio.h>
inline int MAX(int a,int b)
{
    return a>b?a:b;
}
int a[]={9,4,5,5,6,6,63,3};
int max(int n)
{
    return n==0?a[0]:MAX(a[n],max(n-1));
}

int main()
{
    int c;
    c= max(9);
    printf("c=%d\n",c);
    return 0;
}

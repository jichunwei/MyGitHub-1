#include<stdio.h>
int min(int x,int y);
int main()
{
    int a,b,c;
    printf("Please input a & b:");
    scanf("%d %d",&a,&b);
    c=min(a,b);
    printf("c=%d\n",c);
    return 0;
}
int min(int x,int y)
{
    return (x<y?x:y);
}


#include<stdio.h>
int add(int n,...);
int main()
{
    printf("sum1=%d\n",add(3,1,2,3));
    printf("sum2=%d\n",add(5,1,2,3,4,5));
    printf("sum3=%d\n",add(0));
    return 0;
}
    int add(int n,...)
{
    int sum=0,i,*p=&n;
    for(i=1;i<=n;i++)
    sum+=p[i];
    return sum;
}
    



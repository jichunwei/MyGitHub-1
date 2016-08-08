#include<stdio.h>
int main()
{
    int sum,a,b;
    sum=(a=2,b=5,b++,a+b);
    printf("%d\n",sum);
    return 0;
}

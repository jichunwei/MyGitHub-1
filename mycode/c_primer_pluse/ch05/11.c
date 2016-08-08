#include<stdio.h>
int main()
{
    int i=0,count,sum,b;
    sum=0;
    printf("Enter a $ of count:");
    scanf("%d",&count);
    while(++i<=count)
    {
        b=sum+i;
        printf("$%d\n",b);
    }
    printf("\n");
    return 0;
}

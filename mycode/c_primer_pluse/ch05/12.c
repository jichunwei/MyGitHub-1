#include<stdio.h>
int main()
{
    int i,j,sum;
    j=0;
    printf("enter a number of i:");
    scanf("%d",&i);
    while(++j<=i)
    {
        sum=j*j;
        printf("%4d",sum);
    }
    printf("\n");
    return 0;
}


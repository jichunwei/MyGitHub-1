#include<stdio.h>
int main()
{
    int i, j,sum;
    int k=0;
    for(sum=0,i=1;i<=100;i++)
        sum=sum+i;
    printf("%d\n",sum);
    for(i=0,j=100;i<=j;i++,j--)
        k+=i+j;
    printf("%d\n",k);
}

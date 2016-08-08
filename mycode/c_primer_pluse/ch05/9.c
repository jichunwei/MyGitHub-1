#include<stdio.h>
int main()
{
    int i,j=0,b;
    printf("enter a num:");
    scanf("%d",&i);
    while(j<=10)
    {
        j++;
        b=i+j-1;
        printf("%d\n",b);
    }
 return 0;
}

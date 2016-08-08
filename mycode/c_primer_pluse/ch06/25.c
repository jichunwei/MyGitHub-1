#include<stdio.h>
int main()
{
    int i,a=100;
    int n;
    printf("Please input a num:");
    while(scanf("%d",&n)==1)
    {
    for(i=1;i<=n;i++)
        a=a*0.92;
        if(a<=10)
            printf("i=%d",i-1);
        else
            printf("you can do after!\n");
    }
    printf("\n");
    return 0;
}

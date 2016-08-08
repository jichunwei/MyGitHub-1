#include<stdio.h>
int main()
{
    int i,j,t,sum=0;
    for(i=0;i<20;i++)
    {
        printf("please input two num:");
        scanf("%d %d",&j,&t);
        for(i=j;i<=t;i++)
        {
            sum+=i*i;
            printf("index=%d:%3d",i,sum);
            printf("\n");
        }
    }
    return 0;
}

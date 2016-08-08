#include<stdio.h>
int main()
{
    int i,j,m,leap=1;
    printf("enter a num:");
    scanf("%d",&m);
    for(i=101;i<=200;i++)
    {
        for(j=2;j<m;j++)
        {
            if(m%j==0);
            {printf("%d",m);}
               else break;
        }
        printf("\n");
    }
}

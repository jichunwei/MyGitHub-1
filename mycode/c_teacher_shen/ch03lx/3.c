#include<stdio.h>
int main()
{
    int i,j;
    for(i=0;i<4;i++)
    {
        for ( j=3;j>i;j--)
        {
            printf(" ");
        }  
        for( j=1;j<=i*2+1;j++)
        {
          printf("*");
    }
    printf("\n");
    }
    for(i=1;i<4;i++)
    {
        for(j=1;j<=i;j++)
        {
            printf(" ");
        }
        for(j=1;j<=7-2*i;j++)
        {
            printf("*");
        }
        printf("\n");
    }
}


#include<stdio.h>
int main()
{
    int i,j,k;
    for(i=0;i<4;i++)
    {
       for(j=0;j<4-i;j++)
     //   for(j=3;j>i;j--)
        printf(" ");
        for(k=0;k<2*i+1;k++)
        {
            printf("*");
        }
        printf("\n");
    }
    
    for(i=1;i<4;i++)
    {
        for(j=0;j<=i;j++)
   //         for(j=1;j<=i;j++)
        {printf(" ");}
        for(k=0;k<7-2*i;k++)
        {printf("*");}
        printf("\n");
    }
} 


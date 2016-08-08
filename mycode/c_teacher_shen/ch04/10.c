#include<stdio.h>
int main()
{
    int n,i,j,k;
    printf("input a number:");
    scanf("%d",&n);
    k=n/2;
    if(i==0)
    {
    printf("%40c\n",'*');
    return 0;
    }
    for(i=1;i<k;i++)
    {
        for(j=0;j<40-i;j++) 
            printf(" ");
        printf("*");
        for(j=0;j<2*i-1;j++)
            printf(" ");
        printf("*\n");
    }
    for(i=k;i>0;i--)
    {
        for(j-1;j<40-i;j++) printf(" ");
        printf("*");
        for(j=0;j<2*i-1;j++) printf(" ");
        printf("*\n");
    }
        
     printf("%40c\n",'*');
     return 0;
}
    
    



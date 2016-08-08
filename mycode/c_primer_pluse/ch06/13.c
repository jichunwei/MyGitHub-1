#include<stdio.h>
int main()
{
    char ch;
    int i,j;
    printf("input a ch:");
    scanf("%c",&ch);
    char n=ch;
    for(i=0;i<5;i++)
    {
        for(j=4;j>i;j--)
        printf(" ");
        for(j=0,ch=n;j<=i;j++,ch++)
        { 
            {printf("%c",ch);}
        } 
        ch=ch-2;
       for(j=0;j<i;j++,ch--)
           printf("%c",ch);
    //   ch=n;
        printf("\n");
       
    }
    
}

          


            
            

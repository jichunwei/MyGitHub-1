#include<stdio.h>
#include "1.h"
int main()
{
    SqStack sq;
    int c, n;
    InitStack(&sq,100);
    printf("Please input a n:");
    scanf("%d",&n);
    if(n==0)
    {
        printf("0/n");
        return 0;
    }
    if(n<0)
    {
        printf("-");
            n=-n;
    }
    while(n%16!=0)
    {
        c=n%16;
        n=n/16;
        Push(&sq,c);
    }
    while(!EmptyStack(sq))
    {
        Pop(&sq,&n);
        printf("%x",n);
    }
    printf("\n");
    DestroyStack(&sq);
    return 0;
}





#include<stdio.h>
#include "1.h"
int main()
{
    SqStack sq;
    int i,c,n;
    printf("please input a num:");
    scanf("%d",&n);
    if(n==0)
    {
    printf("0\n"); 
    }
    if(n<0)
    {
        n=-n;
        printf("-");
    }

    InitStack(&sq,10);
    while(n%8!=0)
    {
            c=n%8;
            n=n/8;
//            printf("%2d",c);
 //           printf("\n");
            Push(&sq,c);
    }
    while(!EmptyStack(sq))
    {
            Pop(&sq,&c);
        printf("%d",c);
    }
        printf("\n");
        DestroyStack(&sq);
    return 0;
}
       
    

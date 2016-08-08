#include<stdio.h>
#include "1.h"
int main()
{
    SqStack sq;
    int i,d;
    InitStack(&sq,100);
    for(i=1;i<=10;i++)
        Push(&sq,100+i);
    while(!EmptyStack(sq))
    {
        Pop(&sq,&d);
        printf("%d\n",d);
    }
    DestroyStack(&sq);
    return 0;
}
    
            

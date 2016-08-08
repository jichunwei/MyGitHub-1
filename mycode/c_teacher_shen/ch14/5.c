#include<stdio.h>
#include "1.h"
int main()
{
    SqStack sq;
    int i;
    char ch,c;
    InitStack(&sq,100);
    printf("Input a Expr:");
    ch=getchar();
    while(ch!='#')
    {
        if(ch=='(')
        {
            Push(&sq,ch);
        }
        else if(ch==')')
        {
            if(Pop(&sq,&c)==UNDERFLOW)
            {  printf("error!\n");
            return 0;
            }
        //    Pop(&sq,&c);
            
            if(c!='(')
        {
            printf("error!\n");
            return 0;
        }
        }
            else if(ch==']')
            {
                if(Pop(&sq,&c)==UNDERFLOW)
                {
                    printf("error!\n");
                    return 0;
                }
         //       Pop(&sq,&c);
                if(c!='[')
                {
                    printf("error!\n");
                    return 0;
                }
            }
            
            ch=getchar();
    }
        if(!EmptyStack(sq))
            printf("error!\n");
        else printf("ok!\n");
        DestroyStack(&sq);
        return 0;
}

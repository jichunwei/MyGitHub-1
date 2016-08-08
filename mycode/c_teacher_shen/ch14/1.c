/*#define SElemType int 
typedef  enum { SUCCESS,OVERFLOW,UNDERFLOW } Status;
typedef struct{
    SElemType *base;
    SElemType *top;
    int stacksize;
} SqStack;
*/

#include "1.h"
#include<stdio.h>
#include<stdlib.h>

Status InitStack( SqStack *s,int maxsize)
{
    s->base=(SElemType *)malloc(sizeof(SElemType)*maxsize);/*申请分配地址*/
    if(!s->base)
    return OVERFLOW;
    else 
        s->top=s->base;
    s->stacksize=maxsize;
    return SUCCESS;
} 
Status Push(SqStack *s,SElemType e)
{
    if (s->top - s->base == s->stacksize)
        return OVERFLOW;
        *(s->top++)=e;
    return SUCCESS;
}
Status Pop(SqStack *s,SElemType *e)
{
    if(s->top == s->base)
        return UNDERFLOW;
    *e=*(--s->top);
    return SUCCESS;

}
int EmptyStack(SqStack s)
{
    return s.top == s.base;
}
void DestroyStack(SqStack *s)
{
    free(s->base);
    s->top=s->base=NULL;
}






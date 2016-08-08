#include<stdio.h>
#include "2.h"
#include<stdlib.h>

Status Init(LKStack *s)
{
    s->top=NULL;
    return SUCCESS;
}
Status Push(LKStack *s,SElemType e)
{
    struct Node *p;
    p=(struct Node *) malloc(sizeof(struct Node));
    if(!p) return OVERFLOW;
    p->data=e;
    p->next=s->top;
    s->top=p;
    return SUCCESS;
}
Status PoP(LKSack *s,SElemType *e)
{
    struct Node *p;
    if(!s->top)
        return UNDERFLOW;
    *e=s->top->data;
    p=s->top;
    free(p);
    return SUCCESS;
}
int Empty(LkStack s)
{
    return s.top == NULL;
}
voide Destroy(LKStack *s)
{
    struct Node *p;
    while(s->top)
    {
        p=s->top->next;
        free(s->top);
        s->top=p;
    }
}
int Lenght(LKStack s)
{
    struct Node p=s.top;
    int i=0;
    while(p)
    {
        i++;
        p=p->next;
    }
    return i;
}






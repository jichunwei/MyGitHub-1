#include<stdlib.h>
#include"lkqueue.h"
Status InitQueue(LkQueue *q)
{
    q->front=q->rear=(struct Node *)malloc(sizeof(struct Node));
    if(!q->front) return OVERFLOW;
    q->front->next=NULL;
    return SUCCESS;
}
Status EnQueue(LkQueue *q,QElemType e)
{
    struct Node *p;
    p=(struct Node *)malloc(sizeof(struct Node));
    if(!p) return OVERFLOW;
    p->data=e;
    p->next=NULL;
    q->rear=q->rear->next=p;
    return SUCCESS;
}
Status DeQueue(LkQueue *q,QElemType *e)
{
    struct Node *p;
    if(q->front==q->rear) return UNDERFLOW;
    p=q->front;
    *e=p->data;
    q->front->next=p->next;
    if(q->rear==p) q->rear=q->front;
    free(p);
    return SUCCESS;
}
int EmptyQueue(LkQueue q)
{
    return q.front->next==NULL;
}
void  DestroyQueue(LkQueue *q)
{
    struct Node *p;
    while(q->front) {
        p=q->front;q->front=p->next;
        free(p);
    }
}
int LengthQueue(LkQueue q)
{
    int i=0;
    struct Node *p=q.front->next;
    while(p)
    { i++;p=p->next;
    }
    return i;
}

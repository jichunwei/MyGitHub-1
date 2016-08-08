#include<stdio.h>
#include<stdlib.h>
#include "3.h"
Status InitQueue( SqQueue *q,int maxsize)
{
    q->base=(QElemType *)malloc(sizeof(QElemType)*maxsize);
    if(!q->base)
        return OVERFLOW;
    q->front=q->rear=0;
    q->queuesize=maxsize;
    return SUCCESS;
}

Status EnQueue(SqQueue *q,QElemType e)
{
    if((q->rear+1)%q->queuesize==q->front)
        return OVERFLOW;
    q->base[q->rear]=e;
    q->rear=(q->rear+1)%q->queuesize;
    return SUCCESS;
}

Status DeQueue(SqQueue *q,QElemType *e)
{
    if(q->front=q->rear) 
        return UNDERFLOW;
    *e=q->base[q->front];
    q->front=(q->front+1)%q->queuesize;
    return SUCCESS;
}

int EmptyQueue(SqQueue q)
{
    return q.front=q.rear;
}

int FullQueue(SqQueue q)
{
    return (q.rear+1)%q.queuesize==q.front;
}

void DestroyQueue(SqQueue *q)
{
    free(q->base);

}

int LengthQueue(SqQueue q)
{
    return (q.rear+q.queuesize-q.front)%q.queuesize;
}




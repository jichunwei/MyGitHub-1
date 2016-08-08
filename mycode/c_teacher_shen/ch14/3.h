#define QElemType int 
typedef  enum { SUCCESS,OVERFLOW,UNDERFLOW} Status;
typedef struct{
    QElemType *base;
    int front ,rear,queuesize;
}SqQueue;
Status InitQueue( SqQueue *q,int maxsize);
Status EnQueue(SqQueue *q,QElemType e);
Status DeQueue(SqQueue *q,QElemType *e);
int EmptyQueue(SqQueue q);
int FullQueue(SqQueue q);
void DestroyQueue(SqQueue *q);
int LengthQueue(SqQueue q);




#define QElemType int 
typedef enum{SUCCESS,OVERFLOW,UNDERFLOW} Status;
struct Node{
    QElemType data;
    struct Node *next;
};
typedef struct {
    struct Node *front;
    struct Node *rear;
}LkQueue;
Status InitQueue(LkQueue *q);
Status EnQueue(LkQueue *q,QElemType e);
Status DeQueue(LkQueue *q,QElemType *e);
int EmptyQueue(LkQueue q);
void DestroyQueue(LkQueue *q);
int LengthQueue(LkQueue q);

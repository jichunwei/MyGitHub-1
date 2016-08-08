#define SElemType char 
typedef  enum { SUCCESS,OVERFLOW,UNDERFLOW} Status;
typedef struct{
    SElemType *base;
    SElemType *top;
    int stacksize;
} SqStack;
Status InitStack( SqStack *s,int maxsize);
Status Push(SqStack *s,SElemType e);
Status Pop(SqStack *s,SElemType *e);
int EmptyStack(SqStack s);
void DestroyStack(SqStack *s);




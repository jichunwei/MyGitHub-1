#define SElemType int  
typedef  enum { SUCCESS,OVERFLOW,UNDERFLOW} Status;
typedef struct {
    SElemType data;
    struct Node *next;
}Node;
typedef struct{
    Node *top;
    }LkStack;
Status Init( LKStack *s);
Status Push(LKStack *s,SElemType e);
Status Pop(LKStack *s,SElemType *e);
int Empty(LKStack s);
void Destroy(LKStack *s); 
int Lenght(LKStack s);




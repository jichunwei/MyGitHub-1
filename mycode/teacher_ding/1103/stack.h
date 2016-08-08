#ifndef __STACK_H__
#define __STACK_H__
#include "element.h"

struct stack;//前置声明
typedef struct stack Stack;

extern  void push(Stack *s ,ElementType e);
extern ElementType pop(Stack *s);
extern ElementType top(Stack *s);//查看
extern  void  empty(Stack *s);
extern Stack * create(void);
extern void  destroy(Stack *s);
extern int  is_empty(Stack *s);
#endif

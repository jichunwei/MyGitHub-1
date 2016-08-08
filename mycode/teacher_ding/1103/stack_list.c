#include "stack.h"
#include "list.h"
#include <assert.h>
#include <stdlib.h>
#include <malloc.h>

struct stack{
   Node *head; 
    };

void push(Stack *s ,ElementType e)
{
    assert(s != NULL);
    add_list(s->head,e);
}

ElementType pop(Stack *s)
{
    assert(s != NULL);
    Node *p = s->head;//找出尾部的俩个结点
    Node *q = NULL;
    while(p->_next != NULL){
	q = p;
	p = p->_next;
    }
    assert(q != NULL);//
    q->_next = NULL;
    ElementType e = p->_e;
    destroy_list(p);
   // free(p);
    return e;

}

ElementType top(Stack *s)//查看尾部节点
{
    assert( s != NULL);
    int i = size_list(s->head);
    assert(i != 0);
    return get_list(s->head,i - 1);
}

void  empty(Stack *s)
{
    assert(s != NULL);
    if(s->head->_next != NULL)
	destroy_list(s->head->_next);
    s->head->_next = NULL;
}

Stack * create(void)
{
    Stack *s = (Stack*)malloc(sizeof(Stack));
    assert(s != NULL);
    s->head = create_list();
    return s;
}

void  destroy(Stack *s)
{
    destroy_list(s->head);
    free(s);
}
int is_empty(Stack *s)
{
    assert(s != NULL);
    return (s->head->_next == NULL)?1:0;
} 

#include "stdlib.h"
#include "list.h"
#include <assert.h>

Node *create_list(void)
{
    Node *head= (Node *)malloc(sizeof(Node));
    assert( head != NULL);
    head->_next = NULL;
    return head;
}

void destroy_list(Node *head)
{
    assert(head != NULL);
    if(head->_next != NULL)
         destroy_list(head->_next);
    free(head);
}

static Node *tail(Node *head,ElementType e)
{
    if(head->_next == NULL)
        return head;
    return tail(head->_next);
    destroy(head);
}

void add_list(Node *head,ElementType e)
{
    assert(head != NULL);
    Node *t = tail(head);
    Node *p = (Node *)malloc(sizeof(Node));
    p->_e = e;
    p->_next =NULL;
    t->_next = p;
}

static Node *get_pre(Node *head,ElementType e)
{
    if(head->_next == NULL) 
        return 0;
    if(head->_next->_e = e) 
        return head;
    return get_pre(head->_next,e);
}

int remove_list(Node *head,ElementType e)
{
    assert(head != NULL);
    Node *p = get_pre(head,e);
    if(p == NULL)
        return 0;
    Node *f = p->_next;
    *p->_next= p->_next->_next;
    free(f);
    return 1;
}

static Node *indexof(Node *node,int index)
{
    if(node == NULL) return NULL;
    if(index == 0) return node->_next;
    return indexof(node->_next,index - 1);

}

ElementType get_list(Node *head,int index)
{
    assert(head != NULL);
    Node *n = indexof(head,index);
    assert(n != NULL);
    return n->_e;
}

void set_list(Node *head,int index,ElementType e)
{
    assert(head != NULL);
    Node *n = indexof(head,index);
    assert(n != NULL);
    n->_e = e;
}

int size_list(Node *head)
{
    assert(head != NULL);
    if(head->_next == NULL) return 0;
    return size_list(head->_next) + 1;

}

    

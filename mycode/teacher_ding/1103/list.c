#include<stdlib.h>
#include<assert.h>
#include"list.h"

Node* create_list(void)
{
	Node *head=(Node *)malloc(sizeof(Node));
	assert(head!=0);
	head->_next=NULL;
	return head;
}

void destroy_list(Node *head)
{
	assert(head!=0);
//	Node *p=head->_next;
	if(head->_next!=NULL)
		destroy_list(head->_next);
	free(head);
}

static Node* tail(Node *head)
{
	if(head->_next==NULL) return head;
	return tail(head->_next);
}

void add_list(Node *head,ElementType e)
{
	assert(head!=0);
	Node *p=(Node*)malloc(sizeof(Node));
	Node *t=tail(head);
	p->_e=e;
	p->_next=NULL;
	t->_next=p;
}
	
static Node *get_pre(Node *head,ElementType e)
{
	if(head->_next==NULL) return 0; 
	else if(head->_next->_e == e) return head;
	return get_pre(head->_next,e);
}

int remove_list(Node *head,ElementType e)
{
	assert(head != NULL);
	Node *p=get_pre(head,e);
	if(p==NULL) return 0;
	Node *f=p->_next;
	p->_next=p->_next->_next;
	free(f);
	return 1;
}

static Node* indexof(Node *node,int index)
{
	if(node == NULL) return NULL;
	if(index ==0) return node->_next;
   // if(index == 0) return NULL;
	return indexof(node->_next,index-1);

}
ElementType get_list(Node *head,int index)
{
	assert(head!=NULL);
	Node *n=indexof(head,index);
	assert(n != NULL);
	return n->_e;
}
void set_list(Node *head,int index,ElementType e)
{
	assert(head != NULL);
	Node *n=indexof(head,index);
	assert(n != NULL);
	n->_e=e;
}
int size_list(Node *head)
{
	assert(head!=NULL);
	if(head->_next ==NULL) return 0;
	return size_list(head->_next) +1;
}

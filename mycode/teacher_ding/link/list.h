#ifndef __LIST_H__
#define __LIST_H__

typedef int ElementType;

typedef struct node{
	ElementType _e;
	struct node *_next;
}Node;

extern Node* create_list(ElementType e);
extern void destroy_list(Node *head);
extern void add_list(Node *head,ElementType e);
extern Node* remove_list(Node *head,ElementType e);
extern ElementType get_list(Node *head,int index);
extern void set_list(Node *head,int index,ElementType e);
extern int size_list(Node *head);
#endif
#ifndef LIST_H_
#define LIST_H_
enum bool{false,true}
#define TSIZE 45

typedef struct film
{
    char title[TSIZE];
    int rating;
}Item;

//typedef struct film Item;

typedef  struct node{
    Item item;
    struct node *next;
}Node;

typedef Node*  List;

extern void InitializeList(List *plist);
extern bool ListIsEmpty(const List* plist);
extern bool ListIsFull(const List*  plist);
unsigned  int ListItemCount(const List *plist);
extern bool AddItem(Item item,List* plist);
extern void Traverse(const List *plist,void(*pfun)(Item item));
extern void EmptyList(List *plist);
#endif


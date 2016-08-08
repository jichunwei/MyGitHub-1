#ifndef __QUEUE_H__
#define __QUEUE_H__
#include "element.h"


struct queue;
typedef struct queue Queue;
extern void enqueue(Queue *q,ElementType e);
extern ElementType dequeue(Queue *q);
extern int is_queue_empty(Queue *q);
extern ElementType checkQueue(Queue *q);
extern Queue* create_queue(void);
extern void destroy_queue(Queue *q);
extern void empty_queue(Queue *q);

#endif

#include "element.h"
#include "queue.h"
#include <assert.h>
#include <malloc.h>
#include<stdlib.h>
#include "vector.h"


struct queue
{
    vector *v;
};

void enqueue(Queue *q,ElementType e)
{
    assert(q != NULL);
    add_vector(q->v,e);
}

ElementType dequeue(Queue *q)
{
    assert(q != NULL);
    ElementType e = get_vector(q->v,e);
    remove_vector(q->v,e);
    return e;
}

int is_queue_empty(Queue *q)
{
    assert(q != NULL);
    return ((q->v->_counter == 0)?1:0);
   
}

ElementType checkQueue(Queue *q)
{
    assert(q != NULL);
    return get_vector(q->v,0);
}

Queue* create_queue(void)
{
    Queue *q = (Queue*)malloc(sizeof(Queue));
    assert(q != NULL);
    q->v = create_vector(10);
    return q;
}

void destroy_queue(Queue *q)
{
    assert(q != NULL);
    destroy_vector(q->v);
    free(q);
}

void empty_queue(Queue *q)
{
    assert(q != NULL);
    q->v->_counter = 0;
}




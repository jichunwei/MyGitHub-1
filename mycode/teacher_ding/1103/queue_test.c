#include "queue.h"
#include "vector.h"
#include <stdio.h>


int main()
{
    Queue *q = create_queue();
    enqueue(q,1);
    enqueue(q,2);
    enqueue(q,3);
    int i = 0;
    for(; i < 2; i++)
    {
	printf("dequeue(%d): %d\n",i,dequeue(q));
    }
   // empty_queue(q);
    enqueue(q,100);
    enqueue(q,200);
    printf("checkQueue():%d\n",checkQueue(q));
    destroy_queue(q);
    return 0 ;
}

#include "stack.h"
#include <stdio.h>

int main()
{
    Stack *s = create();
    push(s,1);
    push(s,2);
    push(s,3);
    int i = 0;
    for(; i < 2; i++)
    {
	printf("pop(%d): %d\n",i,pop(s));
    }
    empty(s);
    push(s,100);
    push(s,200);
    printf("top():%d\n",top(s));
    destroy(s);
    return 0 ;
}

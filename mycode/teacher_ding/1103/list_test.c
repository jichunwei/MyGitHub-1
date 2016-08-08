#include "list.h"
#include <stdio.h>

void out(Node *v)
{
    int i = 0;
    for(; i < size_list(v); i++)
    {
	if( 0 == i)
	{
	    printf("%d",get_list(v,i));
	}
	else {
	    printf(",%d",get_list(v,i));
	}
    }
    printf("\n");
}
int main()
{
    Node *v = create_list();
    add_list(v,3);//indexof 0
    add_list(v,2);//indexof 1
    add_list(v,1);//indexof 2
    out(v);
    remove_list(v,2);
    out(v);
    set_list(v,0,0);
    out(v);
    printf("first is %d\n",get_list(v,0));
    destroy_list(v);

    return 0;
    
}

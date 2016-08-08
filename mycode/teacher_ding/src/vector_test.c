#include "vector.h"
#include <stdio.h>

void out(vector *v)
{
    int i = 0;
    for(; i < v->_counter; i++)
    {
	if( 0 == i)
	{
	    printf("%d",get_vector(v,i));
	}
	else {
	    printf(",%d",get_vector(v,i));
	}
    }
    printf("\n");
}
int main()
{
    vector *v = create_vector(1);
    add_vector(v,3);//indexof 0
    add_vector(v,2);//indexof 1
    add_vector(v,1);//indexof 2
    out(v);
    remove_vector(v,2);
    out(v);
    set_vector(v,0,0);
    out(v);
    printf("first is %d\n",get_vector(v,0));
    destroy_vector(v);

    return 0;
    
}

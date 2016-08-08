#include "list.h"
#include <stdio.h>
void out(Node *v)
{
	int i;
	while(v){	
		printf("%d\t",v->_e);
		v=v->_next;
	}
	printf("\n");
}

int main(void)
{
	Node *v = create_list(4);
	add_list(v,3);
	add_list(v,2);
	add_list(v,1);
	out(v);
	v=remove_list(v,3);
	out(v);
	set_list(v,0,0);
	out(v);
	printf("first is %d\n",get_list(v,0));
	destroy_list(v);
	return 0;
}

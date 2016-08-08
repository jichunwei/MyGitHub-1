#include <stdio.h>

int main(void)
{
	int		i,m = 5;

	for( i = 0; m--; m < 0)
	{
		i++;
		printf("%d %d\n",i,m);
	}
	
	return 0;
}

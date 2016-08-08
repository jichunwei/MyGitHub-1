#include <stdio.h>

int main(void)
{
	int	 a = 10;
	int  b = 5; 

	if(a > b || a > b++)
		printf("a:%d,b:%d\n",a,b);
	
	return 0;
}

#include <stdio.h>

int main()
{
	static int a[3][3] = {1,3,5,7,9,11,13,15,17},y,x,*p = &a[2][2];

	printf("y:%d,p:%p\n",y,p);
	for(x = 0; x < 3; x++)
		y += *(p-4*x);
	printf("%d\n",y);

	return 0;
}

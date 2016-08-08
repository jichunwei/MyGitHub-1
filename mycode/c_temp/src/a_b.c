#include <stdio.h>
#include <math.h>

int main(void)
{
	int		a , b;
	int		max;

	printf("Please input a and b:\n");
	scanf("%d,%d",&a,&b);
	printf("Before swap\n");
	printf("a:%d,b:%d\n",a,b);
	max = ((a + b) + abs(a - b))/2;
	printf("max is %d\n",max);
	a = a + b;
	b = a - b;
	a = a - b; 
	printf("after swap\n");
	printf("a:%d,b:%d\n",a,b);

	return 0;
}

#include <stdio.h>

int main(void)
{
	unsigned int		x;
	unsigned int		a[10];
	int		i = 0;

	printf("enter a num of x:");
//	printf("q to quit\n");
	scanf("%u",&x);
	for(; i < 5; i++){
		a[i] = x;
		x *= x;
		if(a[i] != 0){
			printf("%u,",a[i]);
		}
	}
	printf("\n");

	return 0;
}

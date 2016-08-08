//计算多项式2x的5次方-4x的4次方＋x的3次方＋3x的平方－2x-6;

#include <stdio.h>

int main(void)
{
	double		x;
	double		sum = 0;
	double		total = 0;
	 
	printf("Please input a num of x:");
	printf("q to quit\n");
	while(scanf("%f",&x) != 0){
		total = x * x + 1;
		sum =  (x + 1)*((total * 2 * (x - 1) * (x - 2) + 1) - 3);
		printf("sum is %f:\n",sum);
		printf("enter next x:");
		printf("q to quit!\n");
	}

	return 0;
}


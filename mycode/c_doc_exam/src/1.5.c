//计算算术平均值和几何平均值。

#include <stdio.h>

int main(void)
{
	float f[5] = {1.5,2.0,6.2,4.3,5};
	float	s;
	float sum = 0.0;
	float total = 1.0;
	int		i;
	float  k;

	for(i = 0; i < 5; i++){
		sum  += f[i];
		total *= f[i];
		printf("%.2f:\n",f[i]);
		printf("sum  is %.2f:\n",sum);
		printf("total is %f:\n",total);
	}
	s = sum / 5 ;
	printf("s is %.2f:\n",s);

	return 0;
}

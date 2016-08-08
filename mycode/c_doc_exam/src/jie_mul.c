#include <stdio.h>

int fun(int x)
{
	return x *= (x-1);
}

int main(void)
{
	int		i;
	int		x;
	int		sum = 0;
	int		total ;
	int		k = 1;
	int		a[32];
	int		n;


	for(i = 0; i < 31; i++){
		sum += k;
		k *= 2;
		//printf("%d:\n",sum);
	}
	printf("sum is %d:\n",sum);

	printf("Please input a num of x:\n");
	scanf("%d",&x);
		n = x;
		for(x,i = 0; x > 1,i<n; x--,i++){
			a[i] = x;
			printf("x:%d,a[%d]:%d\n",x,i,a[i]);
		}
		for(i = 0; i < n; i++){
			n *= a[i];
		}
		printf("n is %d\n",n);

	return 0;
}

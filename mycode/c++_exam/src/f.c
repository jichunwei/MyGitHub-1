#include <stdio.h>

int k ; 
int f(int n)
{
	if(n == 1 || n ==2)
		k = 1;
	else 
		 k = f(n - 1) + f(n - 2);
	return k;
}

int main()
{
	int		n;
	printf("input a num of n:");
	printf("q to quit\n");
	while(scanf("%d",&n) == 1){
		f(n);
		printf("sum is %d\n",k);
		printf("enter next num of n");
		printf("q to quit\n");
	}

	return 0;
}

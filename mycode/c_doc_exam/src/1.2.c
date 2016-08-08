//带余的除法算式。

#include <stdio.h>

int main(void)
{
	int		m;
	int		n;

	printf("Please input two num of m and n:");
	printf("q to quit\n");
	while(scanf("%d,%d",&m,&n) != 0){
		int		r;
		int		q;
		if( m > n){
			q = m / n;
			r = m % n;
		}
		if( r != 0)
			printf("%d = %d * %d + %d:\n",m,q,n,r);
		else
			printf("%d = %d * %d:\n",m,q,n);
		printf("Please enter next m and n:\n");
	}

	return 0;
}

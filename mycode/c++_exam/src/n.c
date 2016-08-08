#include <stdio.h>

int n,t;
int find(int n)
{
	if(n == 1)
		t = 1;
	else{
		t = find(n-1)*n;
	}
	return t;
}

int main(void)
{
	int n;

	scanf("%d",&n);
	find(n);
	printf("n! = %d",t);
}

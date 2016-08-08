//判断整除
#include <stdio.h>

void print1(){
	printf("Yes\n");
}

void print2(){
	printf("No\n");
}

int main(void)
{
	int a,b;

	printf("Please input a,b");
	printf("q to quit!\n");
	while(scanf("%d,%d",&a,&b) != 0){
	if((( a >= b) && ( a % b == 0) && ( b != 0)) || ((a < b) && ( b % a == 0) && (a != 0)))
		print1();
	else 
	{	
		print2();
		printf("a and b is can't be div!\n");
	}
		printf("Please enter a and b again!\n");
//		scanf("%d,%d",&a,&b);
	}

	return 0;
}

#include <stdio.h>

int main(void)
{
	float		a,b,c;

	printf("Please input a,b,c:");
	printf("q to quit\n");
	while(scanf("%f,%f,%f",&a,&b,&c)){
		if(c > a && c > b && a > b){
			if(a + b > c && c - b < a)
				printf("Yes\n");
			else
				printf("No\n");
		}else if( c > a && c > b && b > a){
			if( a + b > c && c - a < b)
				printf("Yes\n");
			else
				printf("No\n");
		}else if(a > b && a > c && b > c){
			if(b + c > a && a - c < b)
				printf("Yes\n");
			else
				printf("No\n");
		}else if(a > b && a > c && b < c){
			if( b + c > a && a - b < c)
				printf("Yes\n");
			else 
				printf("No\n");
		}else if(b > a && b > c && a > c){
			if(a + c > b && b - c < a)
				printf("Yes\n");
			else 
				printf("No\n");
		}else if(b > a && b > c && c > a){
			if(a + c > b && b - a < c)
				printf("Yes\n");
			else
				printf("No\n");
		}
		printf("enter next a,b,c\n");
	}

		/*
		if((a + b > c && (a - c < c)) || ((a + c > b && a - c < b)) ||((b+c>a)&&(b-c<a)))
			printf("Yes\n");
		else 
			printf("No\n");
		printf("enter next a,b,c\n");
	}
	*/

	return 0;
}

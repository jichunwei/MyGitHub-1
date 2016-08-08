#include <stdio.h>

int main(void)
{
	int		year;

	printf("enter the num of year:");
	printf("q to quit\n");
	while(scanf("%d",&year)){
		if((year % 400 == 0) || ((year % 4 == 0) && (year % 100 != 0))){
			printf("The year of %d is a leapyear:\n",year);
		}else
			printf("The year of %d is not a leapyear:\n",year);
		printf("enter next of year:");
	}

	return 0;
}

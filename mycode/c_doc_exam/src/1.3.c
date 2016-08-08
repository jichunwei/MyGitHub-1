//十进制各位数之和
//这个程序的bug就是不能循环输入。
#include <stdio.h>

int main(void)
{
	int		interger;
	int		i = 0;
	int		r[32];
	int		total = 0;
	int		counter = 1;
	int		sum = 0;

	printf("Please input the interge:");
	printf("q to quit\n");
	scanf("%d",&interger);
	for(; i < 32; i++){
		if(interger / 10 > 0){
			r[i] = interger % 10;
			interger = interger / 10;
			counter++;
		}
		//			printf("r[%d]:%d\n",counter-2,r[i]);
	}
	printf("counter:%d,interger:%d,\n",counter,interger);
	i = counter - 2;
	for(; i >= 0; i--){
		total += r[i];
		sum = total + interger;
	}
	if(counter == 1)
		printf("sum is %d:\n",interger);
	else 
		printf("sum is %d:\n",sum);

	return 0;
}

#include <stdio.h>

typedef struct{
	int		x;
	char	y;
}mytype;

int main()
{
	int a = 10;
	typeof(&a)	ptr;
	ptr = &a;
	printf("*ptr:%d\n",*ptr);
//数字可以转换为地址，当不能从中取存数据;
	typeof(((mytype*)0)->y) b;
	b = 'm';
	printf("b;%c\n",b);

	return 0;
}

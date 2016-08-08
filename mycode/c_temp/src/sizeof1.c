#include <stdio.h>

char var[10];
int test(char var[])
{
	return sizeof(var);
}

int main(void)
{
	test(var);
	printf("%d\n",test(var));
}

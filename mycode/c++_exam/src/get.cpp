#include <iostream>
#include <cstring>
#include <cstdlib>
using namespace std;

//可能是乱码，也可能是正常输出，因为fun返回的是指向“栈内存”的指针，该指针的地址不是NULL，但其原来的内容已经被清楚，新内容不可知。
char *fun(void)
{
	char p[] = "hello world";
	return p;
}

int main(void)
{
	char *str = NULL;
	str = fun();
	cout<<str;

	return 0;
}

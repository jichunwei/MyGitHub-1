#include <iostream>
#include <cstdlib>
#include <cstring>

using namespace std;

void GetMemory(char **p,int num)
{
	*p = (char *)malloc(sizeof(char)*num);
}

int main(void)
{
	char *str = NULL;

	GetMemory(&str,100);
	strcpy(str,"hello");
	cout<<*str<<endl;
	cout<<str<<endl;
	cout<<&str<<endl;

	return 0;
}

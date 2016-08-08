#include <iostream>
#include <cstring>
#include <cstdlib>

using namespace std;

char *get_memory(char *p,int num)
{
	p = (char*)malloc(sizeof(char)*num);

	return p;
}

int main(void)
{
	char *str = NULL;

	str = get_memory(str,100);
	strcpy(str,"hello");
	cout<<str<<endl;

	return 0;
}

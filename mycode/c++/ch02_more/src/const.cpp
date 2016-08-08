#include <iostream>
using namespace std;

int main(void)
{
	const int num = 10;
	//num = 20;
	/*
	const int num;
	num = 10;
	*/
	int *p = &num;
	*p = 20;

	cout<<"num:"<<num<<endl;

	return 0;
}

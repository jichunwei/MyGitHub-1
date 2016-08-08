#include <iostream>

using namespace std;

void change(int *a,int &b,int c)
{
	c = *a;
	b = 3;
	*a = 2;
}

int main()
{
	int a = 1,b = 2,c = 3;
	change(&a,b,c);
	cout<<"a:"<<a<<",b:"<<b<<",c:"<<c<<endl;

	return 0;
}

#include <iostream>

using namespace std;

static void swap(int &a,int &b)
{
	int		t;

	t = a;
	a = b;
	b = t;
}

int main(void)
{
	int a = 10;
	int b = 6;
	cout<<"a:"<<a<<",b:"<<b<<endl;
	swap(a,b);

	cout<<"after swap"<<endl;
	cout<<"a:"<<a<<",b"<<b<<endl;
	return 0;
}

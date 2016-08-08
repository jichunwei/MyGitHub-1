#include <iostream>
using namespace std;

template <typename T>
T sum(T t1, T t2)
{
	return t1 + t2;
}

template <typename T>
T sum(T t1,T t2,T t3)
{
	return t1 + t2 + t3;
}


int main(void)
{
	int		a = 1;
	int		b = 2;
	cout<<"sum of "<<a<<" and "<<b<<" is:"<<sum(a,b)<<endl;

	int		c = 3;
	cout<<"sum of "<<a<<" and "<<b<<" and "<<c<<" is:"<<sum(a,b,c)<<endl;

	string	d = "hello ";
	string  e = "world ";

	cout<<"sum of string:"<<sum(d,e)<<endl;

	return 0;
}

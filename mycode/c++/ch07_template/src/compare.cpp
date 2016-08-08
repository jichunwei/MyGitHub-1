#include <iostream>
using namespace std;

//template <typename T>
template <class T>
int	compare(T t1,T t2){
	if(t1 > t2)
		return 1;
	else if(t1 < t2)
		return -1;
	return 0;
}

int main()
{
	int		a = 20;
	int		b = 10;
	cout<<a<<" compare "<<b<<" return:"<<compare(a,b)<<endl;

	double	c = 10.5;
	double  d = 20.5;
	cout<<c<<" compare "<<d<<" return:"<<compare(c,d)<<endl;

	string  e = "abc";
	string  f = "abc";
	cout<<e<<" compare "<<f<<" return:"<<compare(e,f)<<endl;

	return 0;
}

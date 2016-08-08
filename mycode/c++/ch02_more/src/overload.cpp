#include <iostream>

using namespace std;

double average(int a,int b)
{
	return (a + b) / 2;
}

int average(double a,double b)
{
	return (a + b) / 2;
}

int main(void)
{
	int		a = 20;
	int		b = 10;
	double avg = average(a,b);
	cout<<"average of "<<a<<" and "<<b<<" is:"<<avg<<endl;

	double		c = 15.2;
	double		d = 25.4;
	double avg2 = average(c,d);
	cout<<"average of "<<c<<" and "<<d<<" is:"<<avg2<<endl;
	return 0;
}

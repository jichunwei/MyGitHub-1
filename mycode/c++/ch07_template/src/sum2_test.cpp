#include "sum2.h"
#include <iostream>
//#include "sum2.cpp"
using namespace std;


int main(void)
{
	int	 a = 1;
	int  b = 2;
	
	cout<<a<<" and "<<b<<" is:"<<sum(a,b)<<endl;
	
	int	 c = 3;
	cout<<a<<" and "<<b<<" and "<<c<<" is:"<<sum(a,b,c)<<endl;

	string e = "xh";
	string f = "sb";
	cout<<e<<" and "<<f<<" is:"<<sum(e,f)<<endl;

}

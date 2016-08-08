#include <iostream>
using namespace std;

int main(void)
{
	int		a = 10;
	int		b = 5;
	
//	if(a > b || a > b++)
	if(a > b |  a > b++)
		cout<<"a:"<<a<<",b:"<<b<<endl;

	return 0;
}

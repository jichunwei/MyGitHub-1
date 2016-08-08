#include <iostream>
using namespace std;

int main(void)
{
	int num = 123;

	cout.width(10);
	cout.fill('#');
	cout.setf(ios::left);
	cout.setf(ios::hex,ios_base::basefield);
	cout.setf(ios::showbase|ios::uppercase);
	cout<<"num:"<<num<<endl;

	return 0;
}

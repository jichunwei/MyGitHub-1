#include <iostream>

using namespace std;

void fun(string &ref)
{
	ref = "tan";
}

int main(void)
{
	string a  = "tt";
	cout<<"before fun,a:"<<a<<endl;
	fun(a);
	cout<<"after fun,a:"<<a<<endl;

	return 0;
}




#include <iostream>
using namespace std;

int var = 3;
int main(void)
{
	int		var = 10;
	::var++;
	cout<<::var<<endl;
	cout<<var<<endl;

	return 0;
}

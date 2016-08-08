#include <iostream>

using namespace std;

int main(void)
{
	int  a = 10;
	int	 i = 0;
	int	 k[32];

	for(i = 0; i < 32; i++){
		k[i] = a % 2;
		a = a % 2;
	cout<<k[i];
	}
	cout<<endl;
	return 0;
}

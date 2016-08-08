#include <iostream>
using namespace std;

//#define max(a,b) (a >= b? a : b)

inline int max(int i,int j)
{
	return i >= j ? i : j;
}

int main(void)
{
	int		a = 20;
	int		b = 10;

	int larger = max(a++,b);
	cout<<"larger:"<<larger<<endl;

	return 0;
}

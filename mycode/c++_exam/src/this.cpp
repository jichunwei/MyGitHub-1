#include <iostream>

using namespace std;

class point{
	public:
		point(){
			cout<<this<<endl;
			cout<<this+1<<endl;
			cout<<this-1<<endl;
		}
};

int main(void)
{
	point a;
	cout<<&a<<endl;
	return 0;
}

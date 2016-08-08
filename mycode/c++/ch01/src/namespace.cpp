#include <iostream>
using namespace std;

namespace A{
	int	num = 100;
	int	add(int a,int b){
		int		result = 0;
		result = a + b;
		cout<<"in namespace A,result:"<<result<<endl;
		return  result;
	}
}

namespace B{
	int num = 200;
	int add(int a,int b){
		int result = 0;
		result = a + b;
		cout<<"in namespace B,result:"<<result<<endl;
	}
}

using namespace B;

int num = 300;
int add(int a,int b)
{
	int result = 0;
	result = a + b;
	cout<<"in default namespace,result:"<<result<<endl;
}


int main(void)
{
	int a = 10;
	int b = 20;

	cout<<"num:"<<A::num<<endl;
	A::add(a,b);
	cout<<"num:"<<B::num<<endl;
	B::add(a,b);
	cout<<"num:"<<::num<<endl;
	::add(a,b);

	return 0;
}

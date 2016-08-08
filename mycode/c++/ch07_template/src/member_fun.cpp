#include <iostream>
using namespace std;

class A{
	private:
		//...
	public:
		template <typename T>
			void show(T t){
				cout<<"In show(T),t:"<<t<<endl;
			}
};

int main(void)
{
	A a;
	a.show("hello");
	a.show(1000);

	return 0;
}

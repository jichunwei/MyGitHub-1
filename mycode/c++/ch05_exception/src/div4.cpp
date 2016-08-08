#include <iostream>
using namespace std;

class my_exception{
	private:
		string mesg;
	public:
		my_exception(){}
		my_exception(string mesg){
			this->mesg = mesg;
		}
		string what(){
			return this->mesg;
		}
};

float div(int a,int b)
{
	if(b == 0){
		throw my_exception("error: b is zero!");
	}
	return a / b;
}

int main(void)
{
	int a; 
	int b;

	cout<<"Please input a,b:"<<endl;
	while(1){
		cin>>a>>b;
		try{
			int c = div(a,b);
			cout<<"c:"<<c<<endl;
//		}catch(char const*e){
		}catch(my_exception &e){
			cout<<e.what()<<endl;
		}
		cout<<"Please input a, b again:"<<endl;
	}
	cout<<"end main"<<endl;

	return 0;
}

#include <iostream>
using namespace std;


float div(int a,int b)
{
	if(b == 0)
		throw string("error:b is zero!");
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
		}catch(string e){
			cout<<e<<endl;
		}
		cout<<"Please input a, b again:"<<endl;
	}
	cout<<"end main"<<endl;

	return 0;
}
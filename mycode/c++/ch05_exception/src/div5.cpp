#include <iostream>
using namespace std;


float div(int a,int b)
{
	if(b == 0 || b == 1){
		switch(b){
			case 0: throw 1;
			case 1: throw string("b is error!");
		}
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
		}catch(int e){
			cout<<"b should not be zero!"<<endl;
		}catch(string e){
			cout<<e<<endl;
		}
		cout<<"Please input a, b again:"<<endl;
	}
	cout<<"end main"<<endl;

	return 0;
}

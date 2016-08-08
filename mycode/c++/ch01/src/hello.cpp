#include <iostream>
using namespace std;
/*
   *This is my first C++ program
   */

int main(void)
{
	string name = "徐宏!";
	int		age  = 10;
	int		num1,num2;
	int		sum = 0;

	cout<<"Hello world!"<<name<<age<<endl;
	cout<<"name:"<<name<<endl;
	cout<<"age:"<<age<<endl;

	cout<<"Please input two number:";
	cin>>num1>>num2;
	sum = num1 + num2;
	cout<<"sum:"<<sum<<endl;

	return 0;
}

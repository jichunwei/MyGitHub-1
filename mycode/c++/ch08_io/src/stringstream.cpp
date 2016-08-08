#include <iostream>
#include <fstream>
#include <sstream>
using namespace std;

int main(void)
{
	string m = "100 xh 20";
	int		id;
	string name;
	int age;

	istringstream ins(m);
	ins>>id>>name>>age;
	cout<<"id:"<<id<<",name:"<<name<<",age:"<<age<<endl;

	ostringstream outs;
	outs<<"id:"<<id<<",name:"<<name<<",age:"<<age<<endl;
	string buf = outs.str();
	cout<<"buf:"<<buf<<endl;
	
	return 0;
}


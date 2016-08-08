#include "stack.h"
#include <iostream>

using namespace briup;
using namespace std;

int main(void)
{
	stack s;
	s.init();
	s.push(1);
	s.push(2);
	s.push(3);
	s.push(4);
	
	cout<<"first pop:"<<s.pop()<<endl;
	cout<<"second pop:"<<s.pop()<<endl;
	cout<<"top:"<<s.gettop()<<endl;

	s.destroy();
	return 0;
}

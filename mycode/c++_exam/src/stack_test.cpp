#include "stack.h"
#include "stack.cpp"
#include <iostream>

using namespace briup;
using namespace std;

int main(void)
{
	stack<int> s; 
	s.init();
	s.push(1);
	s.push(2);
	s.push(3);
	s.push(4);
	
	cout<<"first pop:"<<s.pop()<<endl;
	cout<<"second pop:"<<s.pop()<<endl;
	cout<<"top:"<<s.gettop()<<endl;

	s.destroy();

	stack<double> s1;
	s1.init();
	s1.push(1.5);
	s1.push(2.5);
	s1.push(3.5);
	s1.push(4.5);

	cout<<"first pop:"<<s1.pop()<<endl;
	cout<<"second pop:"<<s1.pop()<<endl;
	cout<<"top:"<<s1.gettop()<<endl;

	s1.destroy();

	stack<char> s2;
	s2.init();
	s2.push('a');
	s2.push('b');
	s2.push('c');
	s2.push('d');

	cout<<"first pop:"<<s2.pop()<<endl;
	cout<<"second pop:"<<s2.pop()<<endl;
	cout<<"top:"<<s2.gettop()<<endl;

	s2.destroy();
	
	return 0;
	
}

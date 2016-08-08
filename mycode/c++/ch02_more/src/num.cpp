#include <iostream>
#include <cctype>
using namespace std;

bool is_num(char c)
{
	return isdigit(c);
}

/*
inline int is_num(char c)
{
	if(c  >= '0' && c <= '9')
		cout<<"c is num!\n";
	else 
		cout<<"c is not num!\n";
	return c;
}
*/

int main(void)
{
	char ch;

	cin>>ch;
	is_num(ch);
	
	cout<<"ch is a num!"<<endl;
	return 0;
}

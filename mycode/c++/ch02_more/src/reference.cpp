#include <iostream>

using namespace std;
/*
	1)引用必须初始化，
	2)除非引用本身是常量，否则不应用不能初始化为常量。
	*/
int main(void)
{
	int a = 10;
	int &refa = a; 
	a++;
	refa++;
	cout<<"a:"<<a<<",refa:"<<refa<<endl;
	cout<<"a address:"<<&a<<",refa address:"<<&refa<<endl;
	const int &refd = 30 ;//
	cout<<"refd:"<<refd<<endl;
	int  m = 100;
	int &refm = m;
	cout<<"refm:"<<refm<<endl;
	
	int n = 200;
	refm = n;
	cout<<"after change refm:"<<refm<<endl;
	cout<<"m:"<<m<<endl;

	return 0;
}

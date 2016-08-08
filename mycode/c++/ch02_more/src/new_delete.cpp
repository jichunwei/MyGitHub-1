#include <iostream>

using namespace std;

int main(void)
{
	/*
	int	*p1 = new int();
	*p1 = 10;
	*/
	int *p1 = new int(10);
	cout<<"p1 address:"<<p1<<",value:"<<*p1<<endl;
	int *p2 = new int[10];
	int i = 0;
	for(; i < 10; i++){
		p2[i] = i;
	}
	for(int *q = p2; q != p2 + 10; q++){
//		cout<<*q<<" ";
		cout<<"*q:"<<*q; 
	}
	cout<<endl;

	delete p1;
	delete [] p2;
	p1 = NULL;
	p2 = NULL;
	return 0;
}

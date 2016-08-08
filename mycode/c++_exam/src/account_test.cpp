#include "account.h"
#include <iostream>

using namespace std;
double account::rate = 0.05;


int main(void)
{
	account acc1(101,"xh",3000);

	acc1.display();
	sleep(5);
	acc1.withdraw(100.00);
	acc1.display();
	sleep(2);
	acc1.deposit(10.00);
	acc1.display();

	account acc2(102,"tan",100);
	acc2.display();
	sleep(3);
	try{
		acc2.deposit(1000);
		acc2.display();
	}catch(account::my_exception &e){
		cout<<e.what()<<endl;
	}
	try{
		acc2.withdraw(-100);
		acc2.display();
	}catch(int e){
		cout<<"the amt of withdraw should't be lower of zero!"<<endl;
	}


	return 0;
}

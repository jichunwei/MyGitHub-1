#include <iostream>
#include "account.h"

using namespace std;
using namespace briup;

int main(void)
{
//	account acc;
//	acc.init("xh",2000);
//	account acc;
//	account acc(10000);
	account acc("xh",1000);
	cout<<"the user of account:"<<acc.getName()<<endl;
	cout<<"after init,balance:"<<acc.getBalance()<<endl;
	acc.withdraw(500);
	cout<<"after withdraw,balance:"<<acc.getBalance()<<endl;
	acc.deposit(200);
	cout<<"after deposit,balance:"<<acc.getBalance()<<endl;
//	acc.balance = 5000;
//	cout<<"after asign ,balance:"<<acc.getBalance()<<endl;

	return 0;
}

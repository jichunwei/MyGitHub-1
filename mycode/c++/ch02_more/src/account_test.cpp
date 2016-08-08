#include <iostream>
#include "account.h"

using namespace std;
using namespace briup;

int main(void)
{
	account acc;
	acc.init("tan",1000000);
	cout<<"after init,balance:"<<acc.getBalance()<<endl;

	acc.withdraw(500);
	cout<<"after withdram,balance"<<acc.getBalance()<<endl;
	acc.deposit(20000000);
	cout<<"after deposit,balance:"<<acc.getBalance()<<endl;

	return 0;
}

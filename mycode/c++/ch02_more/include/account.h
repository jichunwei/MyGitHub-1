#ifndef __ACCOUNT_H__
#define __ACCOUNT_H__
#include <iostream>

namespace briup{
	struct account{
		std::string name;
		double balance;
		void init(std::string myname,double mybalance){
			name = myname;
			balance = mybalance;
		};
		void withdraw(double amt);
		void deposit(double amt);
		inline double getBalance(){return balance;};
	};
}

#endif

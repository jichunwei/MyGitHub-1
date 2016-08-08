#include <iostream>
#include "account.h"

namespace briup{
	void account::withdraw(double amt){
		if(amt < 0 || amt > balance)
			return;
		balance -= amt;
	}
	void account::deposit(double amt){
		if(amt < 0)
			return;
		balance += amt;
	}
}

/*
namespace briup{
	struct account{
		std::string name;
		double balance;
		void withdraw(double amt);
		void deposit(double amt);
		inline double getBalance(){return balance;};
	}
}

*/

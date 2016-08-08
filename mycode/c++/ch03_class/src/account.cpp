#include "account.h"
#include <iostream>
using namespace std;

namespace briup{
/*		void account::init(std::string name ,double balance)
		{
			this->name = name;
			this->balance = balance;
			cout<<"this name:"<<this->name<<endl;
		}
		*/

		void account::withdraw(double amt)
		{
			if(amt < 0 || amt > this->balance)
				return;
			balance -= amt;
		}

		void account::deposit(double amt)
		{
			if(amt < 0)
				return;
			this->balance += amt;
		}

		void account::destroy()
		{
		}
}



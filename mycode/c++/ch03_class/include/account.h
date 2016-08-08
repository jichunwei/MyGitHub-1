#ifndef __ACCOUNT_H__
#define __ACCOUNT_H__

#include <iostream>
namespace briup{
	class account{
		private:
		std::string name;
		double balance;
		public:
		account(){};
		account(double balance){
			this->balance = balance;
		}
		account(std::string name,double balance)
		{
			this->name = name;
			this->balance = balance;
		}
		//geter,seter function
		std::string getName(){return this->name;};
		void setName(std::string name){this->name = name;};
//		void init(std::string name,double balance);
		void withdraw(double amt);
		void deposit(double amt);
		void destroy();
		double getBalance(){return balance;};
	};
}

#endif


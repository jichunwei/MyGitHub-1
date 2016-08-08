#include "account.h"
#include <iostream>
#include <assert.h>
#include <time.h>
using namespace std;

double account::deposit(double amt)
{
//	assert(amt > 0 && amt <= balance);
	if(amt < 0 || amt >= balance){
		throw my_exception("amt should be regular!");
	}
	time_t t = time(NULL);
	t -= seconds;
	balance = balance *(1+rate*t) - amt;
//	time_t year;
//	year = t / (3600 * 24 * 365);
//	balance = balance *( 1 + rate * year) -amt;
}

double account::withdraw(double amt)
{
//	assert(amt > 0);
	if(amt < 0){
		throw 1;
	}
	time_t t = time(NULL);
	t -= seconds;
	balance = balance*(1+rate*t) + amt;
	/*
	time_t year;
	year = t / (3600 * 24 * 365);
	balance = balance *(1 + year * rate )+ amt;
	*/
}

double account::get_balance()
{
	double balance;
	time_t tm = time(NULL);
	tm -= seconds;
	balance = balance*(1+rate*tm);
	/*
	int year;
	year = tm / ( 3600 * 24 * 365);
	balance =  balance * (1 + rate * year);
	*/
}

void account::display()
{
	cout<<"code:"<<code<<endl;
	cout<<"name:"<<name<<endl;
	cout<<"balance:"<<balance<<endl;
	cout<<"start_date:"<<get_start_date()<<endl;
	cout<<"rate:"<<get_rate()<<endl;
	cout<<"================="<<endl;
}





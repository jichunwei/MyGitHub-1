#ifndef __MONEY_H__
#define __MONEY_H__
#include <iostream>
using namespace std;

class money{
	private:
		double dollar;
		double rmb;
		static double rate;
	public:
		money(){
			this->dollar = 0.00;
			this->rmb = 0.00;
		}
		//explicit money(double dollar){
		money(double dollar){
			this->dollar = dollar;
			this->rmb = dollar * rate;
		}
		money(double amt,bool flag){
			if(flag){
				this->dollar = amt ;
				this->rmb = amt * rate;
			}else {
				this->rmb = amt;
				this->dollar = amt / rate;
			}
		}
		double get_dollar(){return this->dollar;}
		double get_rmb(){return this->rmb;}
		void display(){
			cout<<"dollar:"<<dollar;
			cout<<",rmb:"<<rmb<<endl;
		}
		operator double(){
			return dollar;
		}
};
double money::rate = 7.00;

#endif

#ifndef __ACCOUNT_H__
#define __ACCOUNT_H__
#include <time.h>
#include <assert.h>
#include <iostream>

using namespace std;

class account{
	private:
		int code;
		string name;
		double balance;
		time_t start_date;
		static double rate;
	public:
		time_t seconds;
		class my_exception{
			private:
				string exception;
				int		e;
			public:
				my_exception(){};
				my_exception(string exception){
					this->exception = exception;
				};
				my_exception(int e){
					this->e = e;
				}
				string what(){
					return this->exception;
				};
		};
		account(int code,string name,double balance)
		{
			this->code = code;
			this->name = name;
			this->balance = balance;
			start_date = seconds;
		}
		double get_rate(){
			return this->rate;
		}
		void static set_rate(double new_rate)
		{
			rate = new_rate;
		}
		string get_name(){return this->name;};
		void set_name(string name){
			this->name = name;
		};
		int get_code(){return this->code;};
		void get_code(int code){
			this->code = code;
		};

		double get_balance();
		void set_balance(double balance){
			this->balance = balance;
		};
		string get_start_date()
		{
			seconds = time(NULL);
			cout<<"the seconds of start time:"<<seconds<<endl;
		
			string start_date = ctime(&seconds);
			return start_date;

		};
		void set_start_date(time_t start_date){
			time_t seconds = time(NULL);
			assert(start_date > seconds);
			seconds += start_date;
			char *current_time = ctime(&seconds);
//			this->start_date =  start_date_time;
			cout<<"current time is:"<<current_time<<endl;
		//	time_t	year;
		//	year = seconds / (3600 * 24 * 365);


		};
		double deposit(double amt);
		double withdraw(double amt);
		void display();

};
//double account::rate = 0.05;

#endif


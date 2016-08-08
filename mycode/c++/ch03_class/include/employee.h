#ifndef __EMPLOYEE_H__
#define __EMPLOYEE_H__
#include <iostream>
#include "address.h"

using namespace std;

class employee{
	private:
		int id;
		string name;
		int age;
		double salary;
		address *addr;
	public:
		employee(){};
		employee(int id,int age,string name,double salary){
			this->id = id;
			this->age = age;
			this->name = name;
			this->salary = salary;
		}
		employee(int id,int age,string name,double salary,address *addr){
			this->id = id;
			this->age = age;
			this->name = name;
			this->salary = salary;
			this->addr = addr;
		}
		~employee(){};


		int get_id(){return this->id;}
		void set_id(int id){
			this->id = id;
		}
		string get_name(){return this->name;}
		void set_name(string name){
			this->name = name;
		}
		int get_age(){return this->age;}
		void set_age(int age){
			this->age = age;
		}
		double get_salary(){return this->salary;}
		void set_salary(double salary){
			this->salary = salary;
		}
		address *get_address(){return this->addr;}
		void  set_address(address *addr){
			this->addr = addr;
		}

		void employee_out(){
			cout<<"id:"<<id<<endl;
			cout<<"name:"<<name<<endl;
			cout<<"age:"<<age<<endl;
			cout<<"salary:"<<salary<<endl;
			if(addr != NULL){
				addr->addr_out();
			}
			cout<<"*******************"<<endl;
		};
};

#endif


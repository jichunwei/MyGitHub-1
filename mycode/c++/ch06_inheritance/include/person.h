#ifndef __PERSON_H__
#define __PERSON_H__
#include <iostream>

using namespace std;

class Person{
	protected:
		string		name;
		int			age;
	public:
		Person(){
			cout<<"in Person():"<<endl;
		};
		Person(string name,int age)
		{
			cout<<"in Person(string,int):"<<endl;
			this->name = name;
			this->age = age;
		}
		string get_name(){
			return this->name;
		}
		void set_name(string name){
			this->name = name;
		}
		int get_age(){
			return this->age;
		}
		void set_age(int age){
			this->age = age;
		}
		virtual void talk(){
			cout<<"in Person talk()"<<endl;
		}
		void display(){
			cout<<"name:"<<name;
			cout<<"age:"<<age<<endl;
		}
};

#endif

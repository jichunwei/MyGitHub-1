#ifndef __STUDENT_H__
#define __STUDENT_H__

#include "person.h"

class Student:public Person{
	protected:
		string		school;
		int			id;
		int			age;
		string		name;
	public:
		Student(){
			cout<<"in Student()"<<endl;
		}
		Student(string school,int id):Person("Tom",30)
		{
			//Person("Tom",40);
			cout<<"in Student(string, int)"<<endl;
			this->school = school;
			this->id = id;
		}
		Student(string name,int age,string school,int id):Person(name,age)
		{
			cout<<"in student(string,int,string,int)"<<endl;
			this->school = school;
			this->id = id;
		}


		string get_school(){
			return this->school;
		}
		void set_school(string){
			this->school = school;
		}
		int get_id(){
			return this->id;
		}
		void set_id(int id){
			this->id = id;
		}

		virtual void talk(){
			cout<<"in Student talk(),name:"<<get_name()<<endl;
		}
		void study(){
			cout<<"in stduent study()"<<endl;
			cout<<"==============="<<endl;
		}
};

#endif


#ifndef __STUDENT_H__
#define __STUDENT_H__
#include <iostream>
using namespace std;

class Student{
	private:
		int		id;
		string name;
		int		age;
	public:
		Student(){};
		Student(int id,string name, int age)
		{
			this->id = id;
			this->name = name;
			this->age = age;
		}
	
		void show(){
			cout<<"id:"<<id<<",name:"<<name<<",age"<<age<<endl;
		}
		friend istream &operator >> (istream &is,Student &stu);
		friend ostream &operator << (ostream &os,Student &stu);
};

istream &operator >> (istream &is,Student &stu)
{
	is>>stu.id>>stu.name>>stu.age;

	return is;
}

ostream &operator << (ostream &os,Student &stu)
{
	os<<stu.id<<" "<<stu.name<<" "<<stu.age<<endl;
}

#endif

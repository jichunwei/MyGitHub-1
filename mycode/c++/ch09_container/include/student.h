#ifndef __STUDENT_H__
#define __STUDENT_H__
#include <iostream>
using namespace std;

class Student{
	private:
		int		id;
		string name;
		int age;
	public:
		Student(){}
		Student(int id,string name,int age){
			this->id = id;
			this->name = name ;
			this->age = age;
		}
		friend ostream &operator << (ostream &os,Student &stu);
		bool operator < (Student &s){
			if(this->age < s.age)
				return true;
			return false;
		}
		bool operator > (Student &s){
			if(this->age > s.age)
				return true;
			return false;
		}
		friend bool comp(const Student &s1,const Student &s2);
		friend bool comp1(const Student *s1,const Student *s2);
};

ostream &operator << (ostream &os,Student &stu)
{
	os<<"id:"<<stu.id<<",name:"<<stu.name<<",age:"<<stu.age<<endl;
}

bool comp(const Student &s1,const Student &s2){
	return s1.age > s2.age;
}

bool comp1(const Student *s1,const Student *s2){
	return s1->age < s2->age;
}

#endif

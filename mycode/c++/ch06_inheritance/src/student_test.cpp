#include "person.h"
#include "student.h"

int main(void)
{
	Person p("xh",20);
	p.talk();
	cout<<"********************"<<endl;

	Student s1("Bejing University",10001);
	s1.talk();
	s1.study();

	Student s2("Tom",40,"Qinghua University",10002);
	s2.talk();
	s2.study();

//	s2.name = "jim";
//	s2.talk();
	
	s2.set_name("Jack");
	s2.talk();

	/*
	Person p2 = s2;
	p2.talk();
	p2.study();
	*/

	Person *p3 = new Student("xh1",24,"fudan University",2003);
	p3->talk();

	delete  p3;
	return 0;
}

#include "student.h"
#include <iostream>

using namespace std;
using namespace briup;

int main(void)
{
	student s1(1001);
	student s2(1001,"xh",21,true);
	s2.display();
	s2.setId(1003);
	s2.getId();
	s2.setAge(10);
	s2.getAge();

	//stu.~student();
	student *sp1 = new student(200, "lily",20,false);
	sp1->display();
	student *sp2 = new student(201);
	sp2->setName("kevin");
	sp2->setAge(23);
	sp2->setGender(true);
	sp2->display();

	cout<<"========array======="<<endl;
	student sarray[2];
	sarray[0] = s1;
	sarray[1] = s2;
	sarray[0].display();

	cout<<"********pointer array***********"<<endl;
	student *sparray = new student[2];
	sparray[0] = *sp1;
	sparray[1] = s2;
	sparray[0].display();

	delete [] sparray;
	delete sp1;
	delete sp2;


	return 0;
}



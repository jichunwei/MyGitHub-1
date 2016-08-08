#include <list>
#include "student.h"

void out1(list<Student> &list1)
{
	list<Student>::iterator iter = list1.begin();
	for(; iter != list1.end();iter++){
		cout<<*iter;
	}
}

void out2(list<Student *> &list2)
{
	list<Student*>::iterator iter = list2.begin();
	for(; iter != list2.end(); iter++){
		cout<<**iter;
	}
}

int main(void)
{
	Student s1(100,"tan",24);
	Student s2(101,"xh",23);
	Student s3(102,"wang",22);
	list<Student> list1;
	list1.push_back(s1);
	list1.push_front(s2);
	list1.push_back(s3);
	out1(list1);

	cout<<"==============after sort=============="<<endl;
	//list1.sort();
	list1.sort(comp);
	out1(list1);

	cout<<"===========pointer sort======="<<endl;
	list<Student*> list2;
	Student *sp1 = new Student(104,"Jack",24);
	Student *sp2 = new Student(105,"Jim",34);
	Student *sp3 = new Student(106,"Tom",14);
	list2.push_back(sp1);
	list2.push_back(sp2);
	list2.push_back(sp3);
	list2.sort(comp1);
	out2(list2);



	return 0;
}

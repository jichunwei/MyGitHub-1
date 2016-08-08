#include "student.h"
#include <vector>

void out1(vector<Student> &vec)
{
	vector<Student>::iterator iter = vec.begin();
	for(; iter != vec.end(); iter++){
		cout<<(*iter);
	}
}

void out2(vector<Student *> &vec)
{
	vector<Student *>::iterator iter = vec.begin();
	for(; iter != vec.end(); iter++){
		cout<<(**iter);
	}
}

int main(void)
{
	Student s1(100,"Jack",20);
	Student s2(101,"jim",21);
	Student s3(102,"tan",22);

	vector<Student> vec;
	vec.push_back(s1);
	vec.push_back(s2);
	vec.push_back(s3);
	out1(vec);
	cout<<"============"<<endl;
	Student *sp1 = new Student(100,"Jack",20);
	Student *sp2 = new Student(101,"Jim",21);
	Student *sp3 = new Student(102,"Tom",23);
	vector<Student*> vec2;
	vec2.push_back(sp1);
	vec2.push_back(sp2);
	vec2.push_back(sp3);
	out2(vec2);


	return 0;
}

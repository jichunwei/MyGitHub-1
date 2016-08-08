#include "student.h"
#include <map>

void out1(map<string,Student> &map1){
	map<string,Student>::iterator iter = map1.begin();
	for(; iter != map1.end(); iter++){
		cout<<"key:"<<iter->first<<",value:("<<iter->second<<")"<<endl;
	}
}


int main(void)
{
	Student s1(100,"Jack",20);
	Student s2(101,"jim",21);
	Student s3(102,"tan",22);
	map<string,Student> map1;
//	map1.insert(map<string,Student>::value_type("Jack",s1);
	map1["Jack"]  = s1;
	map1["jim"] = s2;
	map1["Tom"] = s3;
	out1(map1);

	cout<<"find value:"<<map1.find("jim")->second<<endl;


	/*
	cout<<"============"<<endl;
	Student *sp1 = new Student(100,"Jack",20);
	Student *sp2 = new Student(101,"Jim",21);
	Student *sp3 = new Student(102,"Tom",23);
	vector<Student*> vec2;
	vec2.push_back(sp1);
	vec2.push_back(sp2);
	vec2.push_back(sp3);
	out2(vec2);
	*/


	return 0;
}

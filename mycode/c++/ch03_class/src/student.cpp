#include "student.h"
#include <iostream>
using namespace std;

namespace briup{
		void student::display()
		{
			cout<<"stdudent info:"<<endl;
			cout<<"id:"<<id<<endl;
			cout<<"name:"<<name<<endl;
			cout<<"age:"<<age<<endl;
			cout<<"gender:"<<getGender()<<endl;
			cout<<"===================="<<endl;
		};
}


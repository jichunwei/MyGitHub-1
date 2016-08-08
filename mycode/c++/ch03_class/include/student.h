#ifndef __STUDENT_H__
#define __STUDENT_H__

#include <iostream>
using namespace std;
namespace briup{
	class student{
		private:
			int id;
			std::string name;
			int age;
			bool gender;
		public:
			student(){};
			student(int id_no){
				cout<<"in constructor1"<<endl;
				this->id = id_no;
			};
			student(int id,std::string name,int age,bool gender){
				cout<<"in constructor2"<<endl;
				this->id = id;
				this->gender =  gender;
				this->age = age;
				this->name = name;
			};
			/*
			student(student &student)
			{

			}
			*/

			~student()
			{
				cout<<"in deconstructor"<<endl;
			}

			int getId(){return this->id;};

			void setId(int id){this->id = id;};

			std::string getName(){return this->name;};

			void setName(std::string name){this->name = name;}

			int getAge(){return this->age;};

			void setAge(int age){this->age = age;};

			std::string getGender(){
				if(this->gender)
					return "male";
				else
					return "female";
			};

			void setGender(bool gender){
				this->gender = gender;
			}
			void display();
	};
}

#endif

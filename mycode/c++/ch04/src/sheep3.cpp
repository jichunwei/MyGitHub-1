#include <iostream>
#include <string.h>
using namespace std;

class Sheep{
	private:
		char*		name;
		int			age;
	public:
		Sheep(){};
		Sheep(char *name,int age){
			this->name = new char[20];
			strcpy(this->name,name);
			this->age = age;
		}
		Sheep(const Sheep &sheep)
		{
			this->name = new char[20];
			strcpy(this->name,sheep.name);
			this->age = sheep.age;
		}
		~Sheep(){
			delete this->name;
		}

		void display()
		{
			cout<<"name:"<<name;
			cout<<",age:"<<age<<endl;
		}
		char* get_name(){return this->name;};
		void set_name(char* name){
			strcpy(this->name , name);
		}
		int get_age(){return this->age;};
		void set_age(int age){
			this->age = age;
		}
};

int main(void)
{
	Sheep s1("small Sheep",1);
//	Sheep s2(s1);
	Sheep s2 = s1;
	s2.display();
	cout<<"******after change*********"<<endl;
	s2.set_name("big sheep");
	s2.set_age(2);
	s1.display();

	return 0;
}

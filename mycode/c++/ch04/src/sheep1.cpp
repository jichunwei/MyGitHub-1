#include <iostream>
using namespace std;

class Sheep{
	private:
		string		name;
		int			age;
	public:
		Sheep(){};
		Sheep(string name,int age){
			this->name = name;
			this->age = age;
		}
		void display()
		{
			cout<<"name:"<<name;
			cout<<",age:"<<age<<endl;
		}
		string get_name(){return this->name;};
		void set_name(string name){
			this->name = name;
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

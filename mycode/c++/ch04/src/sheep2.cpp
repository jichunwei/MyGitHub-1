#include <iostream>
using namespace std;

class Sheep{
	private:
		string		name;
		int			age;
	public:
		Sheep(){};
		Sheep(const Sheep &sheep)
		{
			cout<<"in copy constructor!"<<endl;
			this->name = sheep.name;
			this->age = sheep.age;
		}

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

void show(Sheep s)
{
	cout<<"in show,name:"<<s.get_name();
	cout<<",age:"<<s.get_name()<<endl;
}

Sheep get_sheep()
{
	Sheep s("xiYangYang",1);
	return s;
}

int main(void)
{
	Sheep s1("small Sheep",1);
	show(s1);
	Sheep s = get_sheep();
	s.display();
//	Sheep s2(s1);
	Sheep s2 = s1;
	s2.display();
	cout<<"******after change*********"<<endl;
	s2.set_name("big sheep");
	s2.set_age(2);
	s1.display();

	return 0;
}

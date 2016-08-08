#include <iostream>
using namespace std;


class student{
	private:
		string name;
		int age;
//		int id;
//		int age;
		static int counter;
	public:
	//	student(){};
		student(string name,int age){
			this->name = name;
			this->age = age;
			counter++;
		}
		~student(){
			counter--;
		}
		void display()
		{
			cout<<"name:"<<name;
			cout<<",age:"<<age<<endl;
			cout<<"+++++++++++++"<<endl;
		}
		static int get_counter()
		{
			return  counter;
		}
};
int student::counter = 0;

int main(void)
{
	student s1("Jack",20);
	student s2("Tom",21);
	s1.display();
	s2.display();
	cout<<"counter:"<<student::get_counter()<<endl;
	cout<<"counter:"<<s1.get_counter()<<endl;
	cout<<"counter:"<<s2.get_counter()<<endl;

	return 0;
}

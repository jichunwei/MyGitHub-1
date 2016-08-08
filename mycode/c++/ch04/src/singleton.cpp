#include <iostream>
using namespace std;

class singleton{
	private:
		static singleton *instance;
//		string name;
//		int		age;
/*		singleton(string name,int age){
			this->age = age;
			this->name = name;
		};
		*/
		singleton(){};
	public:
		static singleton* fun( )
		{
			if(instance == NULL)
				instance = new singleton();
			return instance;
		}
		~singleton(){
			if(instance != NULL)
				delete instance;

		}
/*
		void display()
		{
			cout<<"name:"<<name<<endl;
			cout<<"age:"<<age<<endl;
		}
		*/
};

singleton *singleton::instance = NULL;

int main()
{
	singleton *instance1 = singleton::fun();
	singleton *instance2 = singleton::fun();

	cout<<"instance1:"<<instance1<<endl;
	cout<<"instance2:"<<instance2<<endl;

	return 0;

}

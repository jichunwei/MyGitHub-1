#include <iostream>

using namespace std;

class Girl{
	private:
		string		name;
		int			age;
	public:
		Girl(){};
		Girl(string name,int age)
		{
			this->name = name;
			this->age = age;
		}
		string get_name(){return this->name;};
		void set_name(string name){
			this->name = name;
		};
		int get_age(){return this->age;};
		void set_age(int age){
			this->age = age;
		};
		friend void show(Girl &);
		//void show(Girl &);
};

void show(Girl &girl)
{
	cout<<"name:"<<girl.name<<endl;
	cout<<"age:"<<girl.age<<endl;
}

int main(void)
{
	Girl girl("Lily",20);
	show(girl);

	return 0;
}

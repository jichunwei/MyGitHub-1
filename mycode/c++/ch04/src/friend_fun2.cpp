#include <iostream>

using namespace std;


class Girl{
	private:
		string name;
		int age;
	public:
		Girl(){}
		Girl(string name,int age){
			this->name = name;
			this->age = age;
		}
		friend class Boy;
//		void display(Girl &girl);
};

class Boy{
	private:
		string name;
		int age;
	public:
		Boy(){};
		Boy(string name,int age){
			this->name = name;
			this->age = age;
		}
//		friend class Girl;
	void display(Girl &girl);
};

void Boy::display(Girl &girl)
{
	cout<<"Boy name:"<<name;
	cout<<" age:"<< age<<endl;
	cout<<"Girl name:"<<girl.name;
	cout<<" age:"<< girl.age<<endl;
}

int main(void)
{
	Girl girl("lily",20);
	Boy boy("xh",21);
	boy.display(girl);

	return 0;
}

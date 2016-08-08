#include <iostream>

using namespace std;

class Girl;
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

		void display(Girl &girl);
};


class Girl{
	private:
		string name;
		int  age;
		friend class Boy;
	public:
		Girl(){};
		Girl(string name,int age){
			this->name = name;
			this->age = age;
		}
};
void Boy::display(Girl &girl)
{
	cout<<"Boy name:"<<name;
	cout<<" age:"<<age<<endl;
	cout<<"Girl name:"<<girl.name;
	cout<<" age:"<<girl.age<<endl;
}

int main(void)
{
	Girl girl("Lily",20);
	Boy boy("xh",22);
	boy.display(girl);

	return 0;
}

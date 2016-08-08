#ifndef __MANY_INHERITANCE_H__
#define __MANY_INHERITANCE_H__ 

#include <iostream>
using namespace std;

class Father{
	private:
		string name;
		int age;
	public:
		Father(){
			cout<<"in Father()"<<endl;
		}
		~Father(){
			cout<<"in ~Father()"<<endl;
		}

		virtual void talk(){
			cout<<"in Father talk()"<<endl;
		}
};

class Mother{
	private:
		string name;
		int age;
	public:
		Mother(){
			cout<<"in Mother()"<<endl;
		}
		~Mother(){
			cout<<"in ~Mother()"<<endl;
		}
		//...
		virtual void talk(){
			cout<<"in Mother talk()"<<endl;
		}
};

class Son : public Father,public Mother{
	private:
		//...
	public:
		Son(){
			cout<<"in Son()"<<endl;
		}
		~Son(){
			cout<<"in Son talk()"<<endl;
		}
		virtual void talk(){
			cout<<"in Son talk()"<<endl;
		}
};

#endif

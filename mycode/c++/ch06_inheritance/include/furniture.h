#ifndef __FURNITURE_H
#define __FURNITURE_H
#include <iostream>

using namespace std;

class  Furniture{
	private:
		string name;
	public:
		Furniture(){
			cout<<"In Furniture()"<<endl;
		}
		Furniture(string name){
			cout<<"In Furniture(string)"<<endl;
			this->name = name;
		}
		string get_name(){
			return this->name;
		}
		void set_name(string name){
			this->name = name;
		}
		virtual void display() = 0;
};

class Bed : virtual public Furniture{
	private:
		//...
	public:
		//...
		virtual void display(){
			cout<<"In Bed display()"<<endl;
		}
		virtual void sleep(){
			cout<<"In Bed sleep()"<<endl;
		}
};

class Sofa : virtual public Furniture{
	private:
		//...
	public:
		//...
		virtual void display(){
			cout<<"In Sofa display(),name:"<<get_name()<<endl;
		}
		virtual void sitdown(){
			cout<<"In Sofa sitdown()"<<endl;
		}
};

class Sofa_bed : public Sofa,public Bed{
	private:
		//...
	public:
		//...
		virtual void display(){
			cout<<"In sofa_bed display()"<<endl;
		}
		virtual void sit_sleep(){
			cout<<"In sofa_bed sit_sleep()"<<endl;
		}
};

#endif

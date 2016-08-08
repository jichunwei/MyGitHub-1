#ifndef __AGGREGATION_COMPOSITION__
#define __AGGREGATION_COMPOSITION__
#include <iostream>
using namespace std;

class Computer{
	private:
		string		cpu;
		string		monitor;
	public:
		Computer(){
			cout<<"in Computer()"<<endl;
		};
		Computer(string cpu,string monitor){
			cout<<"in computer(string, string)"<<endl; 
			this->cpu = cpu;
			this->monitor = monitor;
		}
		~Computer(){
			cout<<"in ~Computer()"<<endl;
		}
};

class Heart{
	private:
		//...
	public:
		Heart(){
			cout<<"in Heart()"<<endl;
		};
		~Heart(){
			cout<<"in ~Heart()"<<endl;
		}
};

class Programer{
	private:
		Heart		*heart;
		Computer	*computer;
	public:
		Programer(){
			cout<<"in Programer()"<<endl;
			heart = new Heart();
		}
		~Programer(){
			cout<<"in ~programmer()"<<endl;
			delete heart;
		}
		void set_computer(Computer *computer){
			this->computer = computer;
		}
		void use(){
			cout<<"use computer do something i like"<<endl;
			//调用computer相关操作;
		}
		void live(){
			cout<<"use heart to live"<<endl;
			//调用heart相关操作;
		}
};

#endif

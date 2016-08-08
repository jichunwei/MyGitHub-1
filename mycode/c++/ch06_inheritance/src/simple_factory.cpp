#include <iostream>
using namespace std;

class Car{
	protected:
		string engine;
		string wheel;
	public:
		Car():engine("china"),wheel("shanghai")
	{
		cout<<"in Car()"<<endl;
	}
		Car(string engine,string wheel){
			cout<<"in Car(string,string)"<<endl;
			this->engine = engine;
			this->wheel = wheel;
		}
		/*
		virtual void run(){
			cout<<"the car is running  of xh"<<endl;
		}
		*/
		virtual void run() = 0;
};

class Bmw_car : public Car{
	private:
		string	name;
	public:
		Bmw_car(){};
		Bmw_car(string name){
			this->name = name;
		}
		virtual void run(){
			cout<<"in Bmw_car run()"<<endl;
		}
};

class Benz_car : public Car{
	private:
		//...
	public:
		//...
		virtual void run(){
			cout<<"in Benz_car run()"<<endl;
		}
};

class car_factory{
	public:
		//...
		static Car* create_car(string type)
		{
			if(type == "Bmw_car")
				return new Bmw_car();
			else if(type == "Benz_car")
				return new Benz_car();
			//...
		}
};

int main(void)
{
	Car *mycar = car_factory::create_car("Benz_car");
	mycar->run();

	return 0;
}

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

class Audi_car : public Car{
	private:
		//...
	public:
		//...
		virtual void run(){
			cout<<"in Audi_car run()"<<endl;
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
		virtual Car* create_car() = 0;
};

class Bmw_car_factory : public car_factory{
	public:
	virtual Car *create_car(){
		return new Bmw_car();
	}
};

class Benz_car_factory :public car_factory{
	public:
		virtual Car *create_car(){
			return new Benz_car();
		}
};

class Audi_car_factory : public car_factory{
	public:
		virtual Car* create_car(){
			return new Audi_car();
		}
};

int main(void)
{
	car_factory *factory = new Benz_car_factory();
	Car *mycar = factory->create_car();
	mycar->run();

	car_factory *factory2 = new Audi_car_factory();
	Car *mycar2 = factory2->create_car();
	mycar2->run();

	delete factory;
	delete factory2;
	return 0;
}

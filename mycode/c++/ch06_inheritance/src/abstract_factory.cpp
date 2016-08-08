#include <iostream>
using namespace std;

class Bussiness_car{
	private:
		//...
	public:
		//...
		virtual void run() = 0;
};

class Sport_car{
	private:
		//...
	public:
		//...
		virtual void run() = 0;
};

class Bmw_bussiness_car : public Bussiness_car{
	private:
		//...
	public:
		//...
		virtual void run(){
			cout<<"in Bmw_bussiness_car run()"<<endl;
		}
};

class Benz_bussiness_car : public Bussiness_car{
	private:
		//...
	public:
		//...
		virtual void run(){
			cout<<"in Benz_bussiness_car run()"<<endl;
		}
};

class Bmw_sport_car : public Sport_car{
	private:
		//...
	public:
		//...
		virtual void run(){
			cout<<"in Bmw_sport_car run()"<<endl;
		}
};

class Benz_sport_car : public Sport_car{
	private:
		//...
	public:
		//...
		virtual void run(){
			cout<<"in Benz_sport_car run()"<<endl;
		}
};


class Car_factory{
	public:
		virtual Bussiness_car *create_bussiness_car() = 0;
		virtual Sport_car *create_sport_car() = 0;
};

class Bmw_car_factory : public Car_factory{
	public:
		virtual Bussiness_car *create_bussiness_car()
		{
			return new Bmw_bussiness_car();
		}
		virtual Sport_car *create_sport_car()
		{
			return new Bmw_sport_car();
		}
};

class Benz_car_factory:public Car_factory{
	public:
		virtual Bussiness_car *create_bussiness_car()
		{
			return new Benz_bussiness_car();
		}
		virtual Sport_car *create_sport_car()
		{
			return new Benz_sport_car();
		}
};

int main(void)
{
	Car_factory *factory = new  Benz_car_factory();
	Bussiness_car *mycar = factory->create_bussiness_car();

	mycar->run();

	return 0;
}

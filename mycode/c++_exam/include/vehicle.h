#ifndef __VEHICEL_H__
#define __VEHICEL_H__

#include <iostream>
using namespace std;

class Vehicle{
	protected:
		int		wheels;
		double	weight;
	public:
		Vehicle():wheels(4),weight(1){
			cout<<"in Vehicle()"<<endl;
		}
		Vehicle(int wheels,double weight){
			this->wheels = wheels;
			this->weight = weight;
		}
		//...
		virtual void draw() = 0;
};

class Car : public Vehicle{
	private:
		int		passengers;
	public:
		Car():passengers(20),Vehicle(4,1){
			cout<<"in Car()"<<endl;
		}
		Car(int passengers):Vehicle(4,1){
			this->passengers = passengers;
		}
		virtual void draw() {
			cout<<"in Car:";
			cout<<"passendgers:"<<passengers<<endl;
		};
};

class Truck : public Vehicle{
	private:
		int		passengers;
		double	payload;
	public:
		Truck():passengers(4),Vehicle(4,1),payload(2){
			cout<<"in Truck()"<<endl;
		}
		Truck(int passengers,double payload,int wheels,double weight):Vehicle(wheels,weight)
	{
		cout<<"in Truck(int, double,int,double):"<<endl;
		this->passengers = passengers;
		this->payload = payload;
		this->wheels = wheels;
		this->weight = weight;
	}

		virtual void draw(){
			cout<<"in Truck";
			cout<<"passengers:"<<passengers;
			cout<<",payload:"<<payload<<endl;
		}
};

#endif

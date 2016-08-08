#ifndef __SHAPE_H__
#define __SHAPE_H__
#include <iostream>
using namespace std;

class Shape{
	protected:
		int x;
		int y;
	public:
		Shape():x(0),y(0){
			cout<<"in Shape()"<<endl;
		};
		Shape(int x,int y){
			cout<<"in Shape(int,int)"<<endl;
			this->x = x;
			this->y = y;
		}
		int get_x(){return this->x;};
		void set_x(int x){
			this->x = x;
		}
		int get_y(){return this->y;};
		void set_y(int y){
			this->y = y;
		}
		virtual void draw(){
			cout<<"in Shape draw():"<<endl;
			cout<<"x:"<<x;
			cout<<"y:"<<y;
		}
		virtual double get_area() = 0;
	//		cout<<"in get_area()"<<endl;
		//纯虚函数。
//		virtual double get_area(){};
};

#endif

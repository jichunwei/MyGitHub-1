#ifndef __CIRCLE_H__
#define __CIRCLE_H__
#include "shape.h"
#include <iostream>
#define PI	3.1415926

class Circle:public Shape{
	protected:
		double r;
	public:
		Circle():Shape(0,0),r(1.0){
			cout<<"in circle():"<<endl;
			this->r = r;
		};
		Circle(double r):Shape(0,0){
			cout<<"in Circle(double)"<<endl;
			this->r = r;
		}
		double get_r(){
			return this->r;
		}
		void set_r(double r){
			this->r = r;
		}
		virtual void draw(){
			cout<<"in circle draw, r:"<<r<<endl;
		}
		virtual double get_area(){
			cout<<"in circle get_area():"<<endl;
			return PI*r*r;
		}
};

class Rectangle:public Shape{
	protected:
		double height;
		double width;
	public:
		Rectangle():height(1.0),width(1.0),Shape(0,0){
			cout<<"in Rectangle():"<<endl;
		};

		Rectangle(double height,double width):Shape(0,0){
			cout<<"in Rectangle(double,double):"<<endl;
			this->height= height;
			this->width = width;
		}
		Rectangle(int x,int y,double height,double width):Shape(x,y){
			cout<<"in Rectangle(double,double):"<<endl;
			this->height= height;
			this->width = width;
		}
		double get_height(){
			return this->height;
		}
		void set_height(double height){
			this->height = height;
		}
		double get_width(){
			return this->width;
		}
		void get_width(double width){
			this->width = width;
		}
		virtual void draw(){
			cout<<"height:"<<height;
			cout<<"width:"<<width<<endl;
		}
		virtual double get_area(){
			cout<<"in Rectangle:"<<endl;
			return height*width;
		}

};

#endif

#ifndef __FRACTION_H__
#define __FRACTION_H__
#include <iostream>
using namespace std;

class Fraction{
	private:
		int numerator;
		int denominator;
	public:
		Fraction(){};
		Fraction(int numerator,int denominator){
			this->numerator = numerator;
			this->denominator = denominator;
		};
		int get_numerator(){
			cout<<"numerator:"<<numerator<<endl;
		};
		void set_numerator(int numerator){
			this->numerator = numerator;
		};
		int get_denominator(){
			cout<<"denominator:"<<denominator<<endl;
		};
		void set_denominator(int denominator){
			this->denominator = denominator;
		};

		Fraction operator * (Fraction &fraction){
			this->numerator *= fraction.numerator;
			this->denominator *= fraction.denominator;

			return (*this);
		};

		Fraction operator / (Fraction &fraction){
			this->numerator *= fraction.denominator;
			this->denominator *= fraction.numerator;

			return (*this);
		};

		Fraction operator ++ (int){
			Fraction fraction = *this;
			this->numerator++;
			this->denominator++;

			return fraction;
		};

		Fraction operator ++ (){
			Fraction fraction = *this;

			this->numerator++;
			this->denominator++;

			return (*this);
		}

		bool operator == (Fraction &fraction){
			Fraction f = *this;
			if((this->numerator / this->denominator) == (fraction.numerator / fraction.denominator))
			{
				cout<<"f is equal to fraction!"<<endl;
				return true;
			}
			return false;
			cout<<"f is not equal to fraction!"<<endl;
		};

		int fun(){
			bool flag = true;
			Fraction *f ;
			f->numerator = this->numerator;
			f->denominator = this->denominator;

			if(flag)
				return f->numerator;
			return f->denominator;
		};

		void display(){
			int value = 1;
			for(;value < 1000; value++){
				if(((this->numerator % value ) == 0) && ((this->denominator % value) == 0)){
					this->numerator = this->numerator / value;
					this->denominator = this->denominator / value;
					//	cout<<"this fraction:"<<endl;
					//	cout<<this->numerator<<"/"<<this->denominator<<endl;
				}
			}
			cout<<"this fraction:";
			cout<<numerator<<"/"<<denominator<<endl;
		};
};

#endif

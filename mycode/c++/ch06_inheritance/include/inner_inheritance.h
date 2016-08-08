#ifndef __INNER_INHERITANCE_H__
#define __INNER_INHERITANCE_H__
#include <iostream>

using namespace std;

class Outer{
	private:
		int		value;
	public:
		Outer():value(0){}
		Outer(int value){
			this->value = value;
		}
		class Inner{
			private:
				int		i_value;
			public:
				Inner():i_value(0){}
				Inner(int i_value){
					this->i_value = i_value;
				}
				/*
				virtual void display(){
					cout<<"in Inner display()"<<endl;
				}
				*/
		};
};

class My_outer {
	private:
		int		m;
	public:
		My_outer():m(0){}
		My_outer(int m){
			this->m = m;
		}
		class  My_inner : public Outer::Inner{
			private:
				int		n;
			public:
				My_inner() : n(0){}
				My_inner(int n){
					this->n = n;
				}
				/*
				virtual void display(){
					cout<<"in my_outer display()"<<endl;
				}
				*/
		};
};


#endif

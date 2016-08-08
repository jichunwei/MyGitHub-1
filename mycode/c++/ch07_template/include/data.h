#ifndef __DATA_H__
#define __DATA_H__
#include <iostream>
using namespace std;

template <class P,typename T>
class Data;

template <class P,class T>
ostream& operator << (ostream&,const Data<P,T>&);

template <class P,class T>
istream& operator>>(istream&,const Data<P,T>&);

template <class P,class T>
Data<P,T> operator + (const Data<P,T>&,const Data<P,T>&);

template <typename P,typename T>
class Data{
	friend ostream& operator << <P,T>(ostream &,const Data<P,T>&);
	friend istream& operator >> <P,T>(istream &,const Data<P,T>&);
	friend Data<P,T> operator + <P,T>(const Data<P,T>&,const Data<P,T>&);
	friend class Friend_class;
	private:
		P	id;
		T	code;
	public:
		Data(){
			cout<<"Data() is invoked"<<endl;
		}
		Data(P p,T t):id(p),code(t){
			cout<<"Data(P,T)is invoked"<<endl;
		}
		void set_id(P p);
		P get_id();
		void set_code(T t);
		T get_code();
};

class Friend_class{
	public:
		template <typename P,typename T>
			void display(Data<P,T> &d){
				cout<<"display() is invoked"<<endl;
				cout<<"id:"<<d.id<<" code:"<<d.code<<endl;
			}
};

#include "../src/data.cpp"

#endif

#include "data.h"


template <class P,class T>
ostream& operator << (ostream &os,const Data<P,T> &d)
{
	os<<"operator<<(ostream &,const Data<P,T>&) is invoked"<<endl;
	os<<"id:"<<d.id<<" code:"<<d.code;

//	return os;
}

template <class P,class T>
istream& operator >> (istream &is,const Data<P,T> &d)
{
	is>>d.id>>d.code;
	return is;
}

template <class P,class T>
Data<P,T> operator + (const Data<P,T> &d1,const Data<P,T> &d2)
{
	cout<<"operator<<(const Data<P,T>&,const Data<P,T>& is invoked"<<endl;
	Data<P,T>	d;
	d.id = d1.id + d2.id;
	d.code = d1.code + d2.code;
	return d;
}


template <typename P,typename T>
void Data<P,T>::set_id(P p)
{
	this->id = p;
}

template <typename P,typename T>
P Data<P,T>::get_id()
{
	return this->id;	
}

template <typename P,typename T>
void Data<P,T>::set_code(T t)
{
	this->code = t;
}

template <typename P,typename T>
T Data<P,T>:: get_code()
{
	return this->code;
}




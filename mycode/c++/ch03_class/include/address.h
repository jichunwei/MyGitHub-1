#ifndef __ADDRESS_H__
#define __ADDRESS_H__
#include <iostream>

using namespace std;

class address
{
	private:
		string country;
		string province;
		string city;
		string street;
		unsigned int zip;
	public:
		address(){};
		address(string country,string province,string city,string street,unsigned int zip){
			this->country = country;
			this->province = province;
			this->city = city;
			this->street = street;
			this->zip = zip;
		}
		~address(){};
		string get_country(){return this->country;}
		void set_country(string country)
		{
			this->country = country;
		}
		string get_province(){return this->province;}
		void set_province(string province)
		{
			this->province = province;
		}
		string get_city(){return this->city;}
		void set_city(string city){
			this->city = city;
		}
		string get_street(){return this->street;}
		void set_street(){
			this->street = street;
		}
		unsigned int get_zip(){return this->zip;}
		void set_zip(unsigned int zip){
			this->zip = zip;
		}
		void addr_out()
		{
			cout<<"country:"<<country<<endl;
			cout<<"province:"<<province<<endl;
			cout<<"city:"<<city<<endl;
			cout<<"street:"<<street<<endl;
			cout<<"zip:"<<zip<<endl;
			cout<<"================="<<endl;
		}
};

#endif


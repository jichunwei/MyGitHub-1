#ifndef __MUSIC_H__
#define __MUSIC_H__
#include <iostream>
#include <time.h>
using namespace std;

/*
string get_date()
{
	time_t	t = time(NULL);
	char *s_date = ctime(t);
	return s_date;
}
*/

class Music{
	protected:
		string		author;
		string		name;
		string		date;
	public:
		Music(){
			cout<<"in Music()"<<endl;
		}
		Music(string author,string name,string date){
			this->author = author;
			this->name = name;
			this->date = date;
		}

//		virtual void display() = 0;

		virtual void display(){
			cout<<"author:"<<author<<endl;
			cout<<"name:"<<name<<endl;
			cout<<"date:"<<date<<endl;
		};
};

class Painting : public Music{
	private:
		double	height;
		double  weight;
	public:
		Painting(){
			cout<<"in Painting()"<<endl;
		}
		Painting(double height,double weight){
			this->height = height;
			this->weight = weight;
		}

		virtual void display(){
			cout<<"in Painting display()"<<endl;
			cout<<"height:"<<height;
			cout<<",weight:"<<weight<<endl;
		}
};

class Chamber: public Music{
	private:
		int		persons;
	public:
		Chamber():persons(0){
			cout<<"in Chamber()"<<endl;
		}
		Chamber(int persons){
			cout<<"in Chamber(int):"<<endl;
			this->persons = persons;
		}
		virtual void display(){
			cout<<"in Chamber display()"<<endl;
			cout<<"persons:"<<persons<<endl;
		}
};

#endif

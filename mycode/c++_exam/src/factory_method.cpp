#include <iostream>
using namespace std;

class Airplan{
	protected:
		double		height;
		int			persons;
		//...
	public:
		Airplan(){};
		Airplan(double height,int persons){
			this->height = height;
			this->persons = persons;
		}
		virtual void fly(){
			cout<<"in airplan fly()"<<endl;
		}
	//	virtual void fly() = 0;
};


class Sh_airplan : public Airplan{
	private:
		int persons;
		//...
	public:
		Sh_airplan(int persons){
			this->persons = persons;
		}
		//...
		virtual void fly(){
			cout<<"in Sh_airplan fly()"<<endl;
			cout<<"persons:"<<persons<<endl;
		}
};

class Bj_airplan : public Airplan{
	private:
		//...
	public:
		//...
		virtual void fly(){
			cout<<"in Bj_airplan fly()"<<endl;
		}
};

class Hn_airplan : public Airplan{
	private:
		//...
	public:
		//...
		virtual  void fly(){
			cout<<"in Hn_airplan fly()"<<endl;
		}
};

class Airplan_factory{
	private:
		//...
	public:
		virtual Airplan *create_airplan() = 0;
};

class Bj_airplan_factory : public Airplan_factory{
	private:
		//...
	public:
		//...
		virtual Airplan *create_airplan(){
			cout<<"in Bj_airplan_factory():"<<endl;
			return new Bj_airplan();
		}
};

class Sh_airplan_factory : public Airplan_factory{
	private:
		//...
	public:
		//..
		virtual Airplan *create_airplan(){
			cout<<"in Sh_airplan_factory():"<<endl;
			return new Sh_airplan(10);
		}

};

class Hn_airplan_factory : public Airplan_factory{
	private:
		//...
	public:
		virtual Airplan *create_airplan(){
			cout<<"in Hn_airplan():"<<endl;
			return new Hn_airplan();
		}
};

int main(void)
{
	Airplan_factory  *my_airplan_factory = new Sh_airplan_factory();
	Airplan *my_airplan = my_airplan_factory->create_airplan();
	my_airplan->fly();
	cout<<"================"<<endl;

	
	Airplan_factory *my_airplan_factory1 = new Bj_airplan_factory();
	Airplan *my_airplan1 = my_airplan_factory1->create_airplan();
	my_airplan1->fly();
	cout<<"=================="<<endl;

	return 0;
}

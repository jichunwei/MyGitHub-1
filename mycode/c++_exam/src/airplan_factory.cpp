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

class Airplan_factory{
	private:
		//...
	public:
		static Airplan *create_airplan(string type){
			if(type == "Sh_airplan")
				return new Sh_airplan(10);
			if(type == "Bj_airplan")
				return new Bj_airplan();
		}
};

int main(void)
{
	Airplan *my_airplan = Airplan_factory::create_airplan("Sh_airplan");
	my_airplan->fly();

	return 0;
}

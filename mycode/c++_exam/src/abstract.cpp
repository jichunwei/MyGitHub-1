#include <iostream>
using namespace std;

class Public_plan{
	private:
		//...
	public:
		//...
		virtual void fly() = 0;
};

class Private_plan{
	protected:
		//...
	public:
		//...
		virtual void fly() = 0;
};

class Sh_public_plan : public Public_plan{
	private:
		//...
	public:
		//...
		virtual void fly(){
			cout<<"in Sh_public_plan fly()"<<endl;
		}
};

class Sh_private_plan : public Private_plan{
	private:
		//...
	public:
		virtual void fly(){
			cout<<"In Sh_public_plan fly()"<<endl;
		}
};

class Bj_public_plan : public Public_plan{
	private:
		//...
	public:
		//...
		virtual void fly(){
			cout<<"in Bj_private_plan"<<endl;
		}
};

class Bj_private_plan : public Private_plan{
	private:
		//...
	public:
		virtual void fly(){
			cout<<"In Bj_public_plan"<<endl;
		}
};

class Plan_factory{
	private:
		//...
	public:
		//...
		virtual Public_plan *create_public_plan() = 0;
		virtual Private_plan *create_private_plan() = 0;

};

class Bj_plan_factory : public Plan_factory{
	public:
		virtual Public_plan *create_public_plan(){
	//		cout<<"in Bj_plan_factory"<<endl;
			return new Bj_public_plan();
		}
		virtual Private_plan *create_private_plan(){
			cout<<"in Bj_plan_factory"<<endl;
			return new Bj_private_plan();
		}
};

class Sh_plan_factory : public Plan_factory{
	public:
		virtual Public_plan *create_public_plan(){
			cout<<"in Sh_plan_factory"<<endl;
			return new Sh_public_plan();
		}
		virtual Private_plan *create_private_plan(){
			cout<<"In Sh_plan_factory"<<endl;
			return new Sh_private_plan();
		};
};

int main(void)
{
	Plan_factory *factory1 =  new Bj_plan_factory();
	Public_plan *my_plan = factory1->create_public_plan();
	my_plan->fly();

	Plan_factory *factory2 = new Sh_plan_factory();
	Private_plan *my_plan2 = factory2->create_private_plan();
	my_plan2->fly();

	return 0;
}

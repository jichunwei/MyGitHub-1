#include "vehicle.h"

int main(void)
{
	Vehicle *car1 = new Car();
	car1->draw();
	cout<<"======================"<<endl;

	Vehicle *c2 = new Car(100);
	c2->draw();
	cout<<"======================"<<endl;

	Vehicle *t1 = new Truck();
	t1->draw();
	cout<<"========================"<<endl;

	Vehicle *t2 = new Truck(8,4,8,2);
	t2->draw();
	cout<<"========================"<<endl;

	return 0;
}

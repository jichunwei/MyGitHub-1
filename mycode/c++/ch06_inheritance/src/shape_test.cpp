#include "shape.h"
#include "circle.h"

int main()
{
	/*
	Shape	s1(2,4);
	s1.draw();
	cout<<"================"<<endl;
	*/

	Shape *c1 = new Circle();
//	Circle	c1(2);
	c1->draw();
	cout<<"area:"<<c1->get_area()<<endl;
	cout<<"=================="<<endl;

	Shape *c2 = new Circle(10);
	c2->draw();
	cout<<"area:"<<c2->get_area()<<endl;
	cout<<"=================="<<endl;

	Shape *r1 = new Rectangle();
//	Rectangle	r1(2,5);
	r1->draw();
	cout<<"area:"<<r1->get_area()<<endl;
	cout<<"=================="<<endl;

	Shape *r2 = new Rectangle(10,10);
	r2->draw();
	cout<<"area:"<<r2->get_area()<<endl;
	cout<<"=================="<<endl;

	return 0;
}

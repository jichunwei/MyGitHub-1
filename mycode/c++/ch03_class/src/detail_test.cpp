#include "detail.h"
#include <iostream>

using namespace std;

int main(void)
{
	rectangle rec(4,2);
	
	rec.display();
	rectangle r2;
	r2.change(20,20);
	r2.display();

	/*
	rec.setHeight(3);
	rec.getHeight();
	rec.setWidth(5);
	rec.getWidth();
	rec.display();

	rectangle *r1 = new rectangle(10,10);
	r1->display();
	
	cout<<"===========array==========:"<<endl;
	rectangle ra[3];
	ra[0] = rec;
	ra[1] = *r1;
	ra[0].display();
	ra[2].display();

	cout<<"==========pointer array=========:"<<endl;
	rectangle *rp = new rectangle[2];
	rp[0] = rec;
	rp[1] = *r1;
	rp[0].display();
	rp[1].display();

	delete  [] rp;
	delete r1;
	*/
	return 0;
}

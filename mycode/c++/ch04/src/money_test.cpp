#include "money.h"

int main(void)
{
	money m1(10);
	m1.display();

	money m2(10,true);
	m2.display();

	money m3(70,false);
	m3.display();

	//money m4 = money(10);
	money m4 = 10;
	m4.display();

	double a = m4;
	cout<<"a:"<<m4<<endl;

	return 0;
}

#include "inner.h"
#include <iostream>

using namespace std;

void Outer::display()
{
	Inner in(100);
//	cout<<"in outer dispaly,inner_value:"<<in.inner_value<<endl;
	cout<<"in outer dispaly,inner_value:"<<in.get_inner_value()<<endl;
	cout<<"in outer display,outer_value:"<<outer_value<<endl;
}

void Outer::Inner::display()
{
	cout<<"in innner display,inner_value:"<<inner_value<<endl;
}


void Outer::Inner::display(Outer &outer)
{
	cout<<"in inner display2,outer_value:"<<outer.outer_value<<endl;
	cout<<"in inner display2,outer_value:"<<inner_value<<endl;
}

#include "fraction.h"
#include <iostream>
using namespace std;

int main(void)
{
	Fraction f1(3,4);
	f1.get_numerator();
	f1.display();
	
	Fraction f2(1,2);
	f2.get_denominator();
	f2.display();

	Fraction f3(3,5);
	f3.display();

	cout<<"==========after smaller======"<<endl;
	Fraction f4(2,4);
	f4.display();


	cout<<"========after mul=========="<<endl;
	f1 = f1*(f2);
	f1.display();

	cout<<"===========after div==========="<<endl;
	f3 = f3/(f2);
	f3.display();


	cout<<"==========after f3++=========="<<endl;
	(f3++).display();
	 
	cout<<"==========after ++f3=========="<<endl;
	(++f3).display();

	bool k;
	k = f2 ==(f4);

	return 0;
}

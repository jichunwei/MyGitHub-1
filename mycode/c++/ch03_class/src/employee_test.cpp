//#include "address.h"
#include "employee.h"
//#include <iostream>

using namespace std;

int main(void)
{
	address *addrp = new address("China","HuNan","zhuzhou","chalin Rd",412402);
	employee e1(100,24,"tan",30000);
	e1.set_address(addrp);
	e1.employee_out();

	address addr2("China","ShangHai","ShangHai","WanRong Rd.",20000);
	employee e2(101,23,"xh",5000,&addr2);
	e2.employee_out();

	delete addrp;

	return 0;
}


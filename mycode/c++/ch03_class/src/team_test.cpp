#include "team.h"

using namespace std;
int main(void)
{
	address addr1("china","hunan","zhuzhou","chaling rd",412402);
	employee emp1(101,24,"tan",50000,&addr1);
//	emp1.employee_out();
	address addr2("china","hunan","changsha","yuhua rd",412010);
	employee emp2(102,30,"xh",5922,&addr2);


	team t1;
	t1.addEmployee(emp1);
	t1.addEmployee(emp2);
	t1.team_out();
	t1.removeEmployee(1);
	t1.team_out();
	return 0;
}

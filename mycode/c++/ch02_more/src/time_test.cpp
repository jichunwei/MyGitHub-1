#include "my_time.h"
#include <iostream>
using namespace std;

int main(void)
{
	Time t1(1,30,30);
	Time t2(2,50,34);
	Time t3;
	t3.display();

	t3 = t1.add_time(t2);
	t3.display();
	t3.set_hour(5);
	t3.display();

	t3.reset(0,0,0);
	//t3 = t1.operator + (t2);
	t3 = t1 + t2;

	cout<<"======after reset========="<<endl;
	t3.display();

	cout<<"###########sub test########"<<endl;
	t3.reset(0,0,0);
	t3 = t2 - t1;
	t3.display();

	cout<<"=============++ test########"<<endl;
//	t3++;
	(t3++).display();
	(++t3).display();
//	++t3;
//	t3.display();
	Time t4(1,10,0);
	t3.reset(0,0,0);
//	t3 = t4.operator*(3);
//<=>	t3 = t4 * 3;
	t3 = 3 *t4;  //错误的写法
	t3.display();

	return 0;
}

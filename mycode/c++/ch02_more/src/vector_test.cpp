#include <iostream>
#include "vector.h"

using namespace std;
using namespace briup;

int main(void)
{
	vector	v;
	v.init();
	v.push_back(1);
	v.push_front(3);
	v.insert(2,2);
	v.push_back(4);
	v.push_back(5);
//	v.resize(10);
	v.clear(1);
	v.clear(2,3);
	v.clear();

	cout<<"frist num:"<<v.front()<<endl;
	cout<<"second num:"<<v.get(2)<<endl;
	cout<<"last num:"<<v.back()<<endl;
	cout<<"the num of v:"<<v.size()<<endl;
	cout<<"the maxsize of v:"<<v.maxsize()<<endl;


	v.destory();
	return 0;
}

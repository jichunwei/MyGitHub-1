#include <iostream>
#include <set>
using namespace std;

void out1(set<int> &set1)
{
	set<int>::iterator iter = set1.begin();
	for(; iter != set1.end();iter++){
		cout<<*iter<<endl;
	}
}

int main(void)
{
	set<int> set1;
	set1.insert(1);
	set1.insert(4);
	set1.insert(3);
	set1.insert(3);
	out1(set1);

	cout<<"find:"<<*(set1.find(2))<<endl;
	return 0;
}

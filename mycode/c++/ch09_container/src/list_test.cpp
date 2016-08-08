#include <iostream>
#include <list>

using namespace std;

void out1(list<int> &iList)
{
	list<int>::const_iterator li = iList.begin();
	for(; li != iList.end(); li++){
		cout<<(*li)<<endl;
	}
}

void out2(list<int> &iList)
{
	list<int>::reverse_iterator iter = iList.rbegin();
	for(; iter != iList.rend();iter++){
		cout<<(*iter)<<endl;
	}
}

int main(void)
{
	list<int> ilist;
	ilist.push_back(1);
	ilist.push_back(2);
	ilist.push_front(0);
	ilist.push_back(3);

	cout<<"size:"<<ilist.size()<<endl;
	cout<<"is empty:"<<ilist.empty()<<endl;
	out1(ilist);
	cout<<"=========front,back=========="<<endl;
	cout<<"front:"<<ilist.front()<<endl;
	cout<<"back:"<<ilist.back()<<endl;
	out2(ilist);

	cout<<"============insert============="<<endl;
	list<int>::iterator ci = ilist.begin();
	ci++;
	ci = ilist.insert(ci,10);
	ilist.insert(ci,10);
	out1(ilist);

	cout<<"============erase============="<<endl;
	list<int>::iterator ci1 = ilist.begin();
//	ci1++;
	ilist.erase(ci1);
	out1(ilist);
	cout<<"============sort============="<<endl;
	ilist.sort();
	ilist.unique();
	ilist.reverse();
	out1(ilist);

	return 0;
}

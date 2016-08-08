#include <iostream>
#include <vector> 
using namespace std;

void out1(vector<int> &v)
{
	int		i = 0;

	for(;i < v.size(); i++){
		cout<<"v["<<i<<"]:"<<v[i]<<endl;
	}
}

void out2(vector<int> &v)
{
	int		i = 0;
	for(;  i < v.size();i++){
		cout<<"v["<<i<<"]:"<<v.at(i)<<endl;
	}
}

void out3(vector<int> &vec)
{
	vector<int>::iterator iter = vec.begin();
	while(iter != vec.end()){
		cout<<(*iter)<<endl;
		iter++;
	}
}

void out4(vector<int> &vec)
{
	vector<int>::iterator iter = vec.begin();
	for(iter = vec.begin(); iter != vec.end(); iter++){
		cout<<(*iter)<<endl;
	}
}

int main(void)
{
	vector<int>	vec;
	vec.push_back(1);
	vec.push_back(2);
	vec.push_back(3);
	vec.push_back(5);
//	vec.push_back(4);
//	vec.push_back(4);
//	vec.push_back(4);

	cout<<"size:"<<vec.size()<<endl;
	cout<<"is empty:"<<vec.empty()<<endl;
	out1(vec);
	cout<<"**********font,back***********"<<endl;
	cout<<"fornt:"<<vec.front()<<endl;
	cout<<"back:"<<vec.back()<<endl;
	out2(vec);

	cout<<"**********out3***********"<<endl;
	out3(vec);
//	cout<<"**********out4***********"<<endl;
//	out4(vec);
	cout<<"**********insert***********"<<endl;
	vector<int>::iterator iter = vec.begin();
	iter++;
	iter = vec.insert(iter,10);
	vec.insert(iter,10);
	out3(vec);

	cout<<"*******************delete******************"<<endl;
	//vec.pop_back();
	vector<int>::iterator iter2 = vec.begin();
//	vec.erase(iter2 + 2);
	vec.erase(iter2,iter2 + 3);
	cout<<"iter2:"<<(*iter2)<<endl;
//	*iter2 = 20;
	vec[0] = 20;
	cout<<"iter2:"<<(*iter2)<<endl;
	out3(vec);

	return 0;
}

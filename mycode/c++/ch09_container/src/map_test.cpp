#include <map>
#include <iostream>

using namespace std;

void out1(map<int,string> &map1)
{
	map<int,string>::iterator iter = map1.begin();
	for(; iter != map1.end(); iter++){
		cout<<"key:"<<iter->first<<",value:"<<iter->second<<endl;
	}
}

int main(void)
{
	map<int,string>	map1;
	map1[1] = "Jack";
	map1[2] = "xh";
	map1[4] = "tan";
	map1[3] = "kate";
	out1(map1);

	cout<<"================after insert=========="<<endl;
	map<int,string>::iterator iter = map1.begin();
	iter = map1.insert(iter,pair<int,string>(5,"lily"));
	iter = map1.insert(iter,pair<int,string>(7,"lucy"));
	map1.insert(map<int,string>::value_type(9,"Mary"));
	out1(map1);

	cout<<"===========find================"<<endl;
	cout<<"value:"<<map1.find(5)->second<<endl;

	return 0;
}

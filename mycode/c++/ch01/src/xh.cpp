#include <iostream>
using namespace std;

int main(int argc,char *argv[])
{
	if(argc != 2){
		cout<<"usgname:"<<argv[0]<<endl;
	}
	cin>>argv[1];	
	cout<<"argv[1]:"<<argv[1]<<endl;
	return 0;
}

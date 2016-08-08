#include <iostream>
#include <fstream>
using namespace std;

int main(int argc,char *argv[])
{
	char	buf[256];
//	ifstream	fin(argv[1],ios::in);
	ifstream	fin;
	fin.open(argv[1],ios::in);

	while(fin.getline(buf,256)){
		cout<<"buf:"<<buf<<endl;
	}

	cout<<"=========================="<<endl;
	ofstream fout;
	fout.open(argv[2],ios::out|ios::nocreate);
//	ofstream fout(argv[2],ios::out|ios::trunc);

	fout<<"hello world"<<endl;
	return 0;
}

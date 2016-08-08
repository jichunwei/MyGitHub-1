#include <iostream>
#include <fstream>
using namespace std;

int main(int argc,char *argv[])
{
	char	buf[100];

	ifstream  fin(argv[1],ios::in);
	ofstream fout;
	fout.open(argv[2],ios::out|ios::app);

	while(!fin.eof()){
		fin.getline(buf,100);
			if(isupper(buf[0]))
					fout<<buf<<endl;
	}
	cout<<"==================="<<endl;

	return 0;
}

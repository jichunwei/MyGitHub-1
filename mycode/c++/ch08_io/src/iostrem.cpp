#include <iostream>
#include <fstream>
#include "student.h"
using namespace std;

int main(int argc,char *argv[])
{
	fstream fout(argv[1],ios::out|ios::trunc);
	Student s1(100,"tan",24);
	Student s2(101,"xh",23);
	Student s3(102,"wang",20);
	fout<<s1<<endl;
	fout<<s2<<endl;
	fout<<s3<<endl;

	fout.close();

	cout<<"=============after fout==========="<<endl;

	fstream fin(argv[1],ios::in);
	Student stus[3];
	int	i = 0;
	for(; i < 3; i++){
		fin>>stus[i];
		cout<<stus[i]<<endl;
	}

	return 0;
}

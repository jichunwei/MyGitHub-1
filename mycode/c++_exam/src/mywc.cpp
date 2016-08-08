#include <fstream>
#include <iostream>
using namespace std;

int main(int argc,char *argv[])
{
	char	ch;
	int		chs= 0;
	int		lines = 0;
	int		words = 0;

	if(argc != 2){
		cout<<"-usage:"<<argv[0]<<endl;
		return -1;
	}
	ifstream	fin(argv[1],ios::in);
	while(!fin.eof()){
		if(fin.get() != '\n' && !fin.eof())
		{ 
			chs++;
		}
		else{
			if(!fin.eof())
				lines++;
		}
	}
	/*
	while(!fin.eof()){
		ch = fin.get();
			if((ch>='a')&&(ch <= 'z'))
				words++;
	}
	*/
	cout<<"chs:"<<chs<<endl;
	cout<<"lines:"<<lines<<endl;
	cout<<"words:"<<words<<endl;
	
	return 0;
}

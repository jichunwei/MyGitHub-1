#include "data.h"
#include <fstream>
//#include "data.cpp"

int main(int argc,char *argv[])
{
	Data<int,int> d1;
	d1.set_id(1);
	d1.set_code(100);
	cout<<d1<<endl;
	cout<<"=============="<<endl;

	Data<double,double> d2;
	d2.set_id(2.1);
	d2.set_code(30.01);
	cout<<d2<<endl;
	cout<<"=============="<<endl;
	
	Data<double,double> d3;
	d3.set_id(3.0);
	d3.set_code(20.1);
	cout<<d3<<endl;
	cout<<"=============="<<endl;

	Data<double,double> d4 = d2 + d3;
	cout<<d4<<endl;
	cout<<"=============="<<endl;
	
	Friend_class f;
	f.display(d4);
	cout<<"=============="<<endl;

	Data<int,int> d5[2];
	fstream fin(argv[1],ios::in);
	int i = 0;
	for(; i < 2; i++){
//		fin>>d5[i]; 
		cout<<d5[i]<<endl;
	}

	return 0;
}

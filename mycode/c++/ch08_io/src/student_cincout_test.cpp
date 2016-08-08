#include "student.h"

int main(void)
{
	Student	stu[3];
	int			i = 0;

	for(; i < 3; i++){
		cout<<"Please input student info of three:"<<endl;
		cin>>stu[i];
	}
	cout<<"=======after cin=========="<<endl;

	for(i = 0; i < 3; i++){
		cout<<stu[i]<<endl;
	}

	return 0;
}

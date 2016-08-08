#include <iostream>
using namespace std;

int main(void)
{
	int		num;

	while(cin>>num,!cin.eof()){
		if(cin.good()){
			cout<<"cin good!"<<endl;
			break;
		}
		else if(cin.bad()){
			cout<<"cin bad!"<<endl;
			break;
		}else if(cin.fail()){
			cout<<"cin fail!"<<endl;
			break;
		}else {
			cout<<"num:"<<num<<endl;
			break;
		}
	}

	return 0;
}

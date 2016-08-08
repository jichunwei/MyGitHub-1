#include <iostream>
using namespace std;

int main(void)
{
	int		ch;
	char  ch1;
	char	string[100];

	cout<<"Please input something:";
	ch = cin.get();
	if(ch != EOF)
		cout.put(ch).put('\n');
//		cout<<"ch:"<<(char)ch<<endl;
	//cin.ignore();
//	cin.ignore(100,'\n');
/*	ch1 = cin.peek();
	cout<<"peek() ch1:"<<ch1<<endl;
	*/
	cin.get(ch1);
	if(ch1 != EOF)
		cout<<"ch1:"<<ch1<<endl;
	cin.putback(ch1);
	cin.get(ch1);
	cout.put(ch1).put('\n');

	cin.getline(string,100);//读取一行
//	cin>>string;//遇到空格停止
	cout<<"string:"<<string<<endl;

	/*
	char buffer[10];
	cin.read(buffer,10);
//	cout<<"buffer:"<<buffer<<endl;
	cout.write(buffer,2);
	*/

	return 0;
}

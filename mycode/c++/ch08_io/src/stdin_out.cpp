#include <iostream>
using namespace std;

int main(void)
{
	char	string[100];
	char	buffer[100];
	int		ch;
	char	ch1;

	cin.getline(string,100);
	cout<<"string:"<<string<<endl;

	while((ch = cin.get()) != EOF)
			cout.put(ch);
/*以下是错误的写法。
	cin.read(buffer,100);
	if(cin.get(ch1) == '\n')
		cout.write(buffer,100);
		*/

	return 0;
}

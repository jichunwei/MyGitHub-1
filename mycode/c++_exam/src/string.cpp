#include <iostream>
#include <string>

using namespace std;

int main(void)
{
	string one("xhhaoniubi winner!");
	cout<<one<<endl;
	string two(20,'$');
	cout << two <<endl;
	string three(one);
	cout<<three<<endl;
	one += "oops!";
	cout << one << endl;
	two = "Sorry! That was";
	three[0] = 'P';
	string four;
	four = two + three;
	cout << four <<endl;
	char alls[] = "All's well that end well! ";
	string five(alls,20);
	cout << five << "!\n";
	string six (alls+ 6,alls + 10);
	cout << six << ",";
	string seven (&five[6],&five[10]);
	cout << seven << ",...\n";

	return 0;
}


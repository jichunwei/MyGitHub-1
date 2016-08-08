#include "music.h"
using namespace std;

int main(void)
{
	Music  m1("tan","xhsb","2011,10,17");
	m1.display();
	cout<<"===================="<<endl;

	Painting p1 = Painting(10,20);
	p1.display();
	cout<<"===================="<<endl;

	Painting *p = new Painting(10,10);
	p->display();
	cout<<"===================="<<endl;

	Chamber *c = new Chamber(100);
	c->display();
	cout<<"===================="<<endl;

	return 0;
}

#include "inner.h"
#include <iostream>

using namespace std;

int main(void)
{
	Outer outer(20);
	outer.display();

	Outer::Inner inner(11);
	inner.display();
	inner.display(outer);

	return 0;
}

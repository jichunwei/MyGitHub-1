#include "aggregation_composition.h"

int main(void)
{
	Programer *p = new  Programer();
	p->live();

	Computer *c = new Computer();
	p->set_computer(c);
	p->use();

	delete p;
	delete c;

	return 0;
}

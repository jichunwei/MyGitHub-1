#include "furniture.h"

int main()
{
	Furniture *f = new Bed();
	f->display();

	Furniture *f1 = new Sofa();
	f1->display();

	Furniture *f2 = new Sofa_bed();
	f2->display();

	return 0;
}

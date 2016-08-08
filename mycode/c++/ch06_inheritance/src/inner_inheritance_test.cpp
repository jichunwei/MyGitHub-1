#include "inner_inheritance.h"

int main(void)
{
	My_outer outer;
	Outer::Inner *in = new My_outer::My_inner();

	return 0;
}

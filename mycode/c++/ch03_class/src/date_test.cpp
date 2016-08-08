#include <iostream>
#include "date.h"

using namespace std;

int main(void)
{
	date d1;
	
	d1.date_out();
	d1.set_year(2011);
	d1.set_month(12);
	d1.set_day(31);
	d1.date_out();
	d1.date_next_day();
	d1.date_out();

	date d2(2011,2,29);
	d2.date_out();
	d2.date_next_day();
	d2.date_out();
	
	d2.change_day(2012,2,28);
	d2.date_out();
	d2.date_next_day();
	d2.date_out();
	return 0;
}

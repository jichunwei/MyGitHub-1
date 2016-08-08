#ifndef  __TEAM_H__
#define __TEAM_H__
#include "employee.h"

class team{
	private:
		employee *emps;
		int counter;
		int	max_size;
	public:
		team(){
			emps = new employee[10];
			counter  = 0;
			max_size = 10;
		}
		team(int max_size){
			emps = new employee[max_size];
			counter = 0;
			this->max_size = max_size;
		};

		~team(){
			delete [] emps;
			emps = NULL;
		};

		int size(){return counter;};
		void addEmployee(employee &e);
		void removeEmployee(int index);
		employee& getEmployee(int index);
		void team_out();
};

#endif


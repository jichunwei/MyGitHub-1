//#include "employee.h"
#include "team.h"
#include <iostream>
#include <assert.h>

using namespace std;

void team::addEmployee(employee &e){
	if(counter >= max_size)
		return;
	emps[counter++] = e;
	cout<<"add success!"<<endl;
}

void team::removeEmployee(int index){
	assert(index <= max_size);
	for(index + 1; index < counter; index++){
		emps[index] = emps[index + 1];
	}
	counter--;
	cout<<"remove success!"<<endl;
}

employee& team::getEmployee(int index){
	assert(index <= max_size);
	return emps[index];
	cout<<"get success!"<<endl;
}

void team::team_out(){
	if(counter == 0)
		cout<<"no members in team!"<<endl;
	int i;
	for(i = 0; i< counter; i++){
		emps[i].employee_out();
	}
	cout<<"out success!"<<endl;
}

/*
   class team{
   private:
   employee *emps;
   int counter;
   int	max_size;	
pubilc:
team():max_size(20),counter(0);
team(int max_size){
this max_size = max_size;
};

~team();
int size(){return counter;};
void addEmployee(employee &e);
void removeEmployee(int &index);
employee& getEmployee(int index);
void out();
}
 */



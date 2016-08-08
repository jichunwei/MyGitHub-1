#include <iostream>
#include "student.h"
#include <fstream>
using namespace std;

int main(void)
{
	Student *s = new Student(1,"xh",20);
	ofstream fout("student.bin",ios::out|ios::binary);
	fout.write((char *)s,sizeof(Student));
	fout.flush();
	fout.close();

	ifstream fin("student.bin",ios::in|ios::binary);
	Student *s1 = new Student();
	fin.read((char*)s1,sizeof(Student));
	s1->show();

	return 0;
}


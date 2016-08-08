#include <stdio.h>

struct person{
    char *name;
    int gender;
    int age;
};

int main()
{
    struct persom *p,q;
    p = &q;
    p -> name;
    p -> gender;
    p -> age;
}


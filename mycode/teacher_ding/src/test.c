#include<stdio.h>

int *add(int a,int b)
{
    int sum;
    int *p = &sum;
    sum = a+ b;
    return p;
}

int main()
{
    int *p1,*p2;
    p1= add (3 , 5);
    p2 = add(5,5);
    printf("*p1 is %d and *p2 is %d\n",*p1,*p2);
    return 0;
}


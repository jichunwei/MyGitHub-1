#include<stdio.h>
int main()
{
    int age(int);
    printf("age(5)=%d\n",age(5));
    return 0;
}
int age(int n)
{
    if(n==1) return 10;
    else return age(n-1)+2;
}

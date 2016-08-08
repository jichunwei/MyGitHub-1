#include<stdio.h>
void fun(int a,int b, int c)
{ c=a*b;}
void main()
{
    int c;
    fun (2,3,c);
    printf("%d\n",c);
} 

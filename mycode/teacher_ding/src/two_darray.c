#include<stdio.h>

void out(int *p,int n)
{
    int i = 0;
    for(; i<3;i++)
    {
	printf("%d\n",*(p+2*i));
    }
}
int main()
{
    int d1[6] = { 1,2,3,4,5,6};
    int d2[3][2] = {{ 1,2},{3,4},{5,6}};
	out(d1,6);
	out((int *)d2,6);
	return  0;
} 

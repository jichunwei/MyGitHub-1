#include<stdio.h>
void pounds(int n);
int main()
{
    int times = 5;
    char ch = '!';
    float f = 6.0;
    pounds(times);
    pounds(ch);
    pounds((int) f);
    return 0;
}
void pounds(int n)
{
    while(n-->0)
    {printf("#");
    }printf("\n");
}
    

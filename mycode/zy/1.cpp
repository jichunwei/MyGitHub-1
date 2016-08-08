#include<iostream.h>
using namespace std;
void display(int a,int b=2,int c=3)
{
    printf("a=%d\nb=%d\nc=%d\n",a,b,c);
    
}
int main()
{
    display(1);
    display(1,3);
    display(1,3,7);
    return 0;
}

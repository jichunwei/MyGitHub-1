#include<stdio.h>
int main()
{
    int a=100,b=10;
    int *p1,*p2;
    p1=&a;p2=&b;
    printf("a=%d,b=%d\n",a,b);
    printf("*p1=%d,*p2=%d\n",*p1,*p2);
    printf("&a=%o,&b=%o\n",&a,&b);
    printf("p1=%o,p2=%o\n",p1,p2);
    return 0;
}

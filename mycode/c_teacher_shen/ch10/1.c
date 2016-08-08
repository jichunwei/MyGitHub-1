#include<stdio.h>
union Data{
    int i;
    char c;
    float f;
    }
int main()
{
    union Data a;
    a.f=67.3;
    printf("i=%d c=%c f=%f\n",a.i,a.c,a.f);
}

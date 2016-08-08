#include <stdio.h>

int a[2] = { 1,2};
int b[2] = { 3,4};

int main()
{
    int *p1,*p2,*p3;

    p1 = p2 = a;
    p3 = b;
    printf(" *p1 = %d  *p2 = %d *p3 = %d\n",
            *p1,*p2,*p3);
    printf("*p1++ = %d,*++p2 =%d,(*p3)++ = %d\n",
            *p1++,*++p2,(*p3)++);
    printf(" *p1 = %d  *p2 = %d *p3 = %d\n",
            *p1,*p2,*p3);
    return 0;
}



#include "mmath.h"
#include<stdio.h>

int main()
{
    float f;
    float f1 = 3.14, f2 = 32.2;

    f = add(3.14,32.2);
    printf("add(3.14,32.2) is %f\n",f);
    f = max(3.13,32.2);
    printf("max(3.14,32.2) is %f\n",f);
    return 0;
}

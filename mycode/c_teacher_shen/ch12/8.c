#include "stdio.h"

#define FUDGE(y) (2.84+y)
#define PR(a) printf("%d",(int)(a))
#define PRINT1(a) PR(a);putchar('\n')
 main()
{
    int x=2;
    PRINT1(FUDGE(5)*x);
}

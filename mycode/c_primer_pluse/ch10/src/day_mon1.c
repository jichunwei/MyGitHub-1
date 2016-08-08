#include <stdio.h>
#define MONTHS 12

int main()
{
    int i = 0;
    int day[MONTHS] = { 31,28,31,30,31,30,31,31,30,31,30,31};

    for(; i < MONTHS; i++)
    {
        printf("month %d has %d\n",i+1,day[i]);
    }
    return 0;
}
    


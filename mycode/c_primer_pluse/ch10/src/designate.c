#include <stdio.h>
#define MONTHS 12

int main()
{
    int i;
    int days[MONTHS] = { 31,29,30,[4] =31,[1] = 28};

    for(i = 0; i < MONTHS; i++)
    {
        printf("%2d %d\n",i + 1, days[i]);
    }
    return 0;
}


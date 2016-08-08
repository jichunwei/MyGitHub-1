#include <stdio.h>
#define YEARS 5
#define MONTHS 12

int main()
{
    const float rain[YEARS][MONTHS] = {
        {1.1,2.0,3.2,4.0,5.1,6.1,7.1,8.0,9,10,11,12},
        {1.1,2.0,3.2,4.0,5.1,6.1,7.1,8.0,9,10,11,12},
        {1.1,2.0,3.2,4.0,5.1,6.1,7.1,8.0,9,10,11,12},
        {1.1,2.0,3.2,4.0,5.1,6.1,7.1,8.0,9,10,11,12},
        {1.1,2.0,3.2,4.0,5.1,6.1,7.1,8.0,9,10,11,12}
    };
    int i,j;
    float total ,sum;

    printf("YEARS RAINFALL\n");
    for(i = 0,total = 0; i < YEARS; i++)
    {
        for(j = 0,sum = 0; j < MONTHS; j++)
          sum += rain[i][j];
        printf("%d has %f\n",2000 + i,sum);
        total += sum;
    }
    printf("Ther yearly average is  %.1f inches.\n",total/YEARS);
    printf("MONTHLY AVEARAGES:\n");
    printf(" JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC \n");
    
    for(j = 0; j < MONTHS; j++)
    {
        for(i = 0,sum = 0; i < YEARS; i++)
            sum += rain[i][j];
        printf("%4.1f ",sum/YEARS);
    }
    printf("\n");
    return 0;
}





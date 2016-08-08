#include<stdio.h>
int main()
{
    int days[]={31,28,31,30,31,30,31,31,30,31};
    int index;

    for(index=0;index<sizeof days / sizeof days[1];index++)
    printf("MONTH %d has %d days\n",index+1,days[index]);
    return 0;
}

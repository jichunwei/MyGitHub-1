#include <stdio.h>
#define  SIZE 5 

int sump(int *start,int *end)
{
    int total = 0;
    while(start < end)
    {
        total += *start;
        start++;
    }
    return  total;
}

int main()
{
    int a[SIZE] = { 1,3,5,6,3};
    int k;

    k = sump(a,a + SIZE);
    printf("the total numbers of a is %d\n",k);
    return 0;
}



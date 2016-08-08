#include <stdio.h>
#define SIZE 4

int main()
{
    int date[SIZE];
    int *p1;
    int i;
    double a[SIZE];
    double *p2;
    p1 = date;
    p2 = a;
    
    printf("%23s %10s\n","int","double");
    for(i = 0; i < SIZE; i++)
    {
        printf("pointer + %d %10p %10p\n",i,p1+i,p2+i);
    }
    return 0;
}
        



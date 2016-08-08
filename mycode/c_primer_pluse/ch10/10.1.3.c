#include<stdio.h>
#define SIZE 50
int main()
{
    int i,a[SIZE];
    for(i=0;i<SIZE;i++)
    {
       a[i]=2*i;
    printf("%4d",a[i]);
    if(i%4==0) printf("\n");
    }
    printf("\n");
    return 0;
    
}

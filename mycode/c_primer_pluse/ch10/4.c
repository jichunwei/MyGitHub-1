#include<stdio.h>
#define SIZE 4
int main()
{
    int a[SIZE];
    int i,value1=12,value2=33;
    
    printf("%d %d\n",value1,value2);
    for(i=-1;i<SIZE;i++)
        a[i]=2*i+1;
    for(i=-1;i<7;i++)
        printf("%d %d\n",i,a[i]);
    printf("%d %d\n",value1,value2);
    return 0;
}

    

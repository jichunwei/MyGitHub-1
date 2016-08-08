#include<stdio.h>
int main()
{
    int a[5]={1,2,3,4,5};
    int *num[5]={a+4,a+3,a+2,a+1,a};
    int **p,i;
    p=num;
    for(i=0;i<5;i++)
    { printf("%d\n",**p);
     p++;
    }
    return 0;
}

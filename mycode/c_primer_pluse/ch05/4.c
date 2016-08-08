#include<stdio.h>
int main()
{
    int num=0;
    int n=3,y;
    y=n++ + n++;
    printf("%d %d\n",n,y);
    while(++num<21)
    {
        printf("%10d %10d\n",num,num*num);
        
    }
    return 0;
}

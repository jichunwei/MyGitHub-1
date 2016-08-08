#include<stdio.h>
int main()
{
    int n,i=1,j=2;
    n=i<j?i++:j++;
    printf("%d %d",i,j);
}

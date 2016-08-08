#include<stdio.h>
int main()
{
    long fib(int);
    int n;
    printf("Input n:");
    scanf("%d",&n);
    printf("fib(%d)=%ld\n",n,fib(n));
    return 0;
}
long  fib(int n)
{
        
    if(n<=2)
           return 1;
    else return (fib(n-1)+fib(n-2));
}

#include<stdio.h>
#define k 3.785
#define s 1.609
int main()
{
    float a,b,x;
    printf("Please input a and b:");
    scanf("%d %d",&a,&b);
    x=100*a*k/b*s;
    printf("%0.1f\n",x);
    return 0;
}
     

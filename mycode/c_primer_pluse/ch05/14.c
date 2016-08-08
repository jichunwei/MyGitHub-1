#include<stdio.h>
double f( double t)
{
     double c;
     double k;
    c=t*1.8+32.0;
    k=c+273.16;
    return c,k;
}
int main()
{
   float t1,c1,k1;
   printf("enter the temperatures:");
   scanf("%f",&t1);
   c1=f(t1);
   printf("%.2f is %.2f\n",c1,k1);
   return 0;
}

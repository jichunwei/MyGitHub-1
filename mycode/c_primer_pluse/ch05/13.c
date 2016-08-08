#include<stdio.h>
float f1(float n);
int main()
{
    float i,j;
    printf("Enter a num:");
    scanf("%f",&i);
    j=f1(i);
   printf("%3.1f\n",j);
   return 0;
}
float f1(float n)
{
   float k; 
    k=n*n*n;
    return k; 
}


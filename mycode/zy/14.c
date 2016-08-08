#include<stdio.h>
#define PI 3.14
int main()
{
    float r,s=0,v=0;

    printf("input the r:");
        scanf("%f",&r);
       s=PI*r*r*r;
       v=4*r*r/3;
       printf("%f,%f",s,v);
}
        

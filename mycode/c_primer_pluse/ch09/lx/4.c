#include<stdio.h>
double jz(double x,double y);
int main()
{
//    int m,n;
 //   printf("input two nums:");
  //  scanf("%d %d",&m,&n);
   // printf("%d %d\n",m,n);

    float  a,b,c;
    printf("enter a & b:");
    scanf("%f %f",&a,&b);
    printf("a=%2.2f b=%2.2f\n",a,b);
    c=jz(a,b);
    printf("*********\n");
    printf("c=%f\n",c);
    return 0;
}
double jz(double x,double y)
{
    double z,k;
    z=1/x+1/y;
    k=1/z;
    return k;
}

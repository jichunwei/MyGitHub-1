#include<stdio.h>
int main()
{
    float fun(float a,float b);
    float a,b,s;
    int i,ch;
    for(i=0;i<10;i++)
    {
        printf("enter two numbers:");
        scanf("%f %f",&a,&b);
      s= fun(a,b);
    printf("%4.2f",s);
    scanf("%f %f",&a,&b);
    printf("\n");
    }
    return 0;
}
float fun(float a,float b)
{
    double s;
    s=(a-b)/(a*b);
    return s;
}

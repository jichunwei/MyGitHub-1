#include<stdio.h>
#define G 10.00
#define RATE1 0.15 
#define RATE2 0.20
#define RATE3 0.25
#define k 1.5
int main()
{
    int i,n;
    float b,c, sum=0.00;
    printf("Please input the n:");
   while( scanf("%d",&n)==1)
   {
        if(n>0 && n<=40)
        {   sum=n*G; 
        printf("sum=%4.2f\n",sum);
        }
        else
        {    sum=40*G+(n-40)*k*G;
        printf("sum=%4.2f\n",sum);
        }

    printf("***********\n");
    if(sum<=300)
    { 
        b=sum*RATE1;
    printf("b=%4.2f\n",b);
    }
    if(sum>300&&sum<450)
    {
        b=sum*RATE2;
    printf("b=%4.2f\n",b);
    }
    else
    {
        b=sum*RATE3;
    printf("b=%4.2f\n",b);
    }
    c=sum-b;
    printf("c=%4.2f\n",c);
   printf("***********\n");
   }
    return 0;
}

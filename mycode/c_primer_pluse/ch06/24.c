#include<stdio.h>
//#include<math.h>
int main()
{
     int n,i;
    float  a=100,b=0;
    float c=a;
   printf("please input a num:");
//   scanf("%d",&n);
   while( scanf("%d",&n)==1)
   {
       for(i=1;i<=n;i++)
    {
        b=c+c*0.1*i;
        a=a*(1.05);
    }
       if(a>=b)
    printf("i=%d b=%.2f a=%.2f\n",i-1,b,a);
       else 
           printf("you num is so wrong\n");
  }
     printf("\n");
            return 0;
}


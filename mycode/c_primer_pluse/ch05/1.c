#include<stdio.h>
#define A 60
int main()
 {
     int sec,min,hours,left;
     printf("convert seconds to minutes and second:\n");
     printf("Enter the number of seconds:\n");
     scanf("%d",&sec);
     while(sec>0)
     {
        hours=sec/(A*A);
         min=sec/A;
         left=sec%A;
         printf("%d seconds is %d hours, %d minutes,%d seconds\n",sec,hours,min,left);
         printf("Enter next value (<=0 t0 quit)\n");
         scanf("%d",&sec);
     }
     printf("done!\n");
     return 0;
 }


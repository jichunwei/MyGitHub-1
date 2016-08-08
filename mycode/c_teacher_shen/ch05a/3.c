#include<stdio.h>
int main()
{
   float *search(float(*p)[4],int n);
   float score[][4]={{31,53,87,92},{33,87,22,55},{77,44,99,65}};
       float *p;
       int i,k;
       printf("enter the No.%d's score:\n");
       scanf("%d",&k);
       p=search(score,k);
       for(i=0;i<4;i++)
           printf("%5.2f\t",p[i]);
       printf("\n");
       return 0;
} 
   float *search(float(*p)[4],int n)
   {
       float *pt;
       pt=*(p+n);
       return pt;
   }
       

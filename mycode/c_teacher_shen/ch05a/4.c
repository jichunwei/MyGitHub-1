#include<stdio.h>
int main()
{
    float *search(float (*)[4]);
    float score[][4]={{93,23,53,66},{100,75,99,88},{43,99,3,99}};
    float *p;
    int i,j;
    for(i=0;i<3;i++)
    {
        p=search(score+i);
            if(p!=NULL)
            {
                printf("No.%d:",i);
                for(j=0;j<4;j++)
                    printf("%6.2f",p[j]);
                printf("\n");
            }
    }
    return 0;

}
float *search(float (*p)[4])
{
    int i;
   float *pt=NULL;
   for(i=0;i<4;i++)
       if (*(*p+i)<60) {pt=*p;break;}
   return pt;
}
    

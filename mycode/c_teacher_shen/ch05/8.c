#include<stdio.h>
int main()
{
    int a[3][4]={1,3,5,6,5,3,3,2,14,43,4,4};
    int (*p)[4],i,j;
    p=a;
    printf("enter row and colum:");
    scanf("%d,%d",&i,&j);
    printf("a[%d,%d]=%3d\n",i,j,*(*(p+i)+j));
    return 0;
}

        
  /*  for(p=a[0];p<a[0]+12;p++)
    {
        if((p-a[0])%4==0) printf("\n");
                printf("%4d",*p);
                } 
                printf("\n");
                return 0;
                }
                */

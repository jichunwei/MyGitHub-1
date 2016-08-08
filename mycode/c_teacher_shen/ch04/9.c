#include<stdio.h>
int main()
{
    int i,j, a[2][2]={1,2,3,4};
    int max,row,col;
    for(i=0;i<2;i++)
    {
        for(j=0;j<2;j++)
            printf("%3d",a[i][j]);
        printf("\n");
    }
  for(i=0;i<2;i++)
    {
    max=a[0][0];row=0;col=0;
        for(j=1;j<2;j++)
   if(a[i][j]>max)
    { max=a[i][j];row=i;col=j;
        printf("%3d" ,max);
    }
    printf("\n");
    }
}        
        


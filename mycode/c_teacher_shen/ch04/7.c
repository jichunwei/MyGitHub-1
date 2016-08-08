#include<stdio.h>
int main()
{
    int a[2][2]={1,2,3,4},b[2][2]={2,3,4,5};
    int i,j, c[2][2];
    for(i=0;i<2;i++)
    {
        for(j=0;j<2;j++)
    {
        c[i][j]=a[i][j]+b[i][j];
       printf("%3d",c[i][j]);
    }
    printf("\n");
    }
}


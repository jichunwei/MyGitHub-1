#include<stdio.h>
int main()
{
    int i,j,a[i][j];
    for(i=1;i<10;i++)
    {
        for(j=1;j<10;j++)
        {
            a[i][j]=i*j;
            printf("%3d",a[i][j]);
        }
        printf("\n");
    }
}

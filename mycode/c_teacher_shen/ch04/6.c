#include<stdio.h>
int main()
{
    int a[3][2]={1,2,3,4,5,6},b[2][3],i,j;
    for(i=0;i<3;i++)
    {
        for(j=0;j<2;j++)
        {  b[j][i]=a[i][j];
                printf("%3d",a[i][j]);
    }
    printf("\n");
}
printf("b:\n");
for (i=0;i<2 ;i++)
{
    for (j=0;j<3;j++) printf("%3d",b[i][j]);
    printf("\n");
}
return 0;
}

#include<stdio.h>
int main()
{
    int i,j;
    int a[2][2]={{1,3},{2,3}};
    for(i=0;i<2;i++)
    { for(j=0;j<2;j++)
         printf("%4d",a[i][j]);
        printf("\n");
    }
        
    printf("%d,%d\n",a,*a);
    printf("%d,%d\n",a[0],*(a+0));
    printf("%d,%d\n",&a[0],&a[0][0]);
    printf("%d,%d\n",a[1],a+1);
    printf("%d,%d\n",&a[1][0],*(a+1)+0);
    return 0; 
}

#include<stdio.h>
int main()
{
    int i,j,m;
    for(i=1;i<10;i++)
    {
        for(j=1;j<=i;j++)
        {
            m=i*j;
            printf("i*j=%-3d",i,j,m);
        }
        printf("\n");
    }
    
    return 0;
}

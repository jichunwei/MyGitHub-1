#include<stdio.h>
int main()
{
    int a[5][3]={{1,1,1},{2,4,16},{3,9,27},{4,16,64},{5,25,125}};
    int i,j;
    int c,b;
    for(i=0;i<5;i++)
    { for(j=0;j<3;j++)
        {  printf("%4d",a[i][j]);}
            printf("\n");
    } 
    printf("enter two num:");
    scanf("%d %d",&c,&b);
    for(i=c;i<=b;i++)
    { for(j=0;j<4;j++)
      { printf("%4d",a[i][j]);}
    printf("\n");
    }
    return 0;
}


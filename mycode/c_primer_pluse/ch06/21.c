#include<stdio.h>
int main()
{
/*    int i,a[8];
    printf("enter some nums:");
    for(i=0;i<8;i++)
    {
        scanf("%d",&a[i]);
    }
    for(i=0;i<8;i++)
    {  printf("%5d",a[i]);
    }
    printf("\n");
    */
    int i;
    int a=1,b[8];
    for(i=0;i<8;i++)
    { 
        a*=2;
        b[i]=a;
        printf("%5d",b[i]);
    }
        printf("\n");
    return 0;
}
        

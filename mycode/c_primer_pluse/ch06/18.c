#include<stdio.h>
int main()
{
    int a[10];
    int i,j,t;
    printf("Please input ten num:");
    for(i=0;i<10;i++)
    scanf("%3d",&a[i]);
    for(i=0;i<10;i++)
    printf("%3d",a[i]);
    printf("\n");
    
    for(i=9;i>=0;i--)
    {
        printf("%2d",a[i]);
    }
        printf("\n");
       
    return 0;
  
}
        
        


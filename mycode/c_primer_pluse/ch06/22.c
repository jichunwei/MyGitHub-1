#include<stdio.h>
int main()
{
    int i,j,a[8],b[8];
    printf("Please input eight num:");
    for(i=0;i<8;i++)
    scanf("%d",&a[i]);
    for(i=0;i<8;i++)
    printf("%3d",a[i]);
     printf("\n");
     b[0]=a[0];
     for(i=1;i<=8;i++)
     {
     b[i]=b[i-1]+a[i];
     }
    for(i=0;i<8;i++)
    {
       printf("i=%d a[i]:%d",i,a[i]);
       printf("i=%d b[i]:%d",i,b[i]);
      printf("\n");
       if((i+1)%4==0)
           printf("\n");
     }
    
     //  printf("\n");
      return 0;
}
            
    
    


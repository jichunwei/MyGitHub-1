#include<stdio.h>
int main()
{
    int i,j,n;
    int p=1;
    printf("Please input an num:");
    printf("enter q to quit.\n");
    scanf("%d",&n);
    for(i=2;i<=n;i++)
    {
        for(j=2,p=1;j*j<=i;j++)
          if(i%j==0)
          {
              printf("%d can diver%d and i/j=%d\n",i,j,i/j);
              printf("************\n");
              p=0;
          }
    if(p)
        printf("%d is prime.\n",i);
    }
    printf("Bye!\n");
    return 0;
}
    

#include<stdio.h>
#define N 5
int main()
{
    int t,i,j,a[N];
    for(i=0;i<N;i++)
    {
    printf("enter these num:");
    scanf("%d",&a[i]);
    }
    for(i=0;i<N;i++)
        printf("%4d",a[i]);
    printf("\n");
    for(i=0;i<N-1;i++)
    {
        for(j=0;j<N-i;j++)
            if(a[j]>a[j+1])
            {
                t=a[j];a[j]=a[j+1];a[j+1]=t;
            }
    }
    for(i=0;i<N;i++)
        printf("%4d",a[i]);
    printf("\n");
}
    

        
    
        

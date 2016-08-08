#include<stdio.h>
#define N 8
int main()
{
    int a[N],i,j,t;
    for(i=0;i<N;i++)
    {  
        printf("please enter date:");
    scanf("%d",&a[i]);
    }
    for(i=0;i<N;i++) 
        printf("%4d",a[i]);
    printf("\n");
    for(i=0;i<N;i++)
    { 
        for(j=1;j<N-i;j++)
            if(a[j-1]>a[j])
            {t=a[j-1];a[j-1]=a[j];a[j]=t;}
    } 
    for(i=0;i<N;i++)
        printf("%4d",a[i]);printf("\n");
}


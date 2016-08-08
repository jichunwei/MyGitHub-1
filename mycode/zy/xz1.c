#include<stdio.h>

#define N 5
int main()
{
    int a[N]={1,5,2,4,7};
    int i;
    for(i=0;i<N;i++)
    {
        int j=0;
        for( j=0;j<N-1;j++)
        {
        if(a[j]>a[j+1])
        {
            int temp;
            temp=a[j];a[j]=a[j+1];a[j+1]=temp;
        }
    }

    }    
for(i=0;i<N;i++)
printf("a[i]=%d\n",a[i]);
return 0;
}

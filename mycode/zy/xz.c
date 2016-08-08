#include<stdio.h>
#define N 5
int main()
{
    int a[5]={20,40,-50,7,13};
    int min, k,i;
    for( i=0;i<N-1;i++)
    {
        min=a[i]; k=i;
        int j;
        for( j=i+1;j<N;j++)
        {
            if(min>a[j])
            { min=a[j]; k=j;}
        }
        a[k]=a[i]; a[i]=min;
    }
    for(i=0;i<N;i++)
        printf("a[i]=%d\n",a[i]);
return 0;
}


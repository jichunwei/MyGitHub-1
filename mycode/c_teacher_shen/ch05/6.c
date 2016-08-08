#include<stdio.h>
int fun( int *a,int n)
{
    int i,j,t;
    for(i=0;i<9;i++)
    {
        for(j=0;j<9;j++)
        {
        if(a[j]<a[j+1])
        {  t=a[j];a[j]=a[j+1];a[j+1]=t;}
        }
    }
        printf("\n");
}
    
    
int main()
{
    int i,a[10]={1,5,6,4,5,6,6,7,9,8};
    for (i=0;i<10;i++)
        printf("%3d",a[i]);
    printf("\n");
    fun( a, 10);
        for(i=0;i<10;i++)
        printf("%3d",a[i]);
        printf("\n");
    return 0;
}

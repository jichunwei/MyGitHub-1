#include<stdio.h>
int main()
{
    void qsort(int arr[],int,int);
    int a[]={44,65,33,66,21,66,43,34,55,55};
    int i;
    for(i=0;i<10;i++)
    printf("%4d",a[i]);
    printf("\n");
    qsort(a,0,9);
    for(i=0;i<10;i++) printf("%4d",a[i]);
    printf("\n");
    return 0;
}
void qsort(int arr[],int start ,int end)
{
    int t=arr[start],i=start,j=end;
    while(i<j)
    {
        while(i<j && arr[j]>t) j--;
        if(i<j) {arr[i]=arr[j]; i++;}
        while(i<j  && arr[i]<t) i++;
        if(i<j) { arr[j]=arr[i];j--;}
    }
    arr[i]=t;
    if(start<i-1) qsort(arr,start,i-1);
    if(i+1<end) qsort(arr,i+1,end);
}

    



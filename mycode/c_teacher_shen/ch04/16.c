#include<stdio.h>
int main()
{
    int a[8]={17,25,39,41,58,62,75,84},key,i=0,j=7,m;
    printf("input a key:");
        scanf("%d",&key);
    while(i<=j)
    {
        m=(i+j)/2;
        if(a[m]==key) break;
        else if(a[m]>key) j=m-1;
        else i=m+1;
    }
    if(i>j) printf("-1\n");
    else printf("%d\n",m);
    return 0;
}

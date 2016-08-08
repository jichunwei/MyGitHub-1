#include<stdio.h>
int main()
{
    float i,j;
    int n=5,a=-1;
    for(i=1,j=0;i<n;i++)
    {
        j+=1/i;
        printf("%4.2f\n",j);
    }
    printf("\n");
    for(i=1,j=0,a=-1;i<n;i++)
    { 
        a=a*(-1);
        j+=a/i;
        printf("%4.2f\n",j);
    }
    printf("\n");
    return 0;
}

#include<stdio.h>
#define N 8
int main()
{
    int a[N]={1,155,343,-52,51,-14,53,3},i,j,t;
    printf("0");
/*    for(i=1;i<=N;i++) printf("%4d",a[i]);
    printf("\n");
        for(i=2;i<=N;i++)
        { a[0]=a[i];
            j=i;
            while(a[j-1]>a[j])
            {a[j]=a[j-1];
                j--;
            }
            a[j]=a[0];
            printf("%4d",a[i]);
            printf("\n");
        }
}*/
    for(i=0;i<N;i++) printf("%4d",a[i]);printf("\n");
    for(i=1;i<N;i++)
{    t=a[i];
        j=i;
        while (j>0&&a[j-1]>t)
        {
            a[j]=a[j-1];
            j--;
        }
        a[j]=t;
        printf("%d:",i+1);
        for(j=0;j<N;j++) printf("%4d",a[j]);
        printf("\n");
   
}
}
   

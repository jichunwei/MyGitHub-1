#include<stdio.h>
int main()
{
    int max4(int a,int b,int c,int d);
    int a,b,c,d,max;
    printf("enter 4 num:");
    scanf("%d %d %d %d",&a,&b,&c,&d);
    max=max4(a,b,c,d);
    printf("%d\n",max);
    return 0;
}
int max4(int a,int b,int c,int d)
{
    int i,t,m[4];
    for(i=0;i<4;i++)
        if(m[i]<m[i+1])
        {t=m[i];m[i]=m[i+1];m[i+1]=t;
            printf("%d",m[i]);
        }
    printf("\n");
    return 0;
}





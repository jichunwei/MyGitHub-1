#include<stdio.h>
int main()
{
   /* int m,i;
    int b=0;
    printf("please input a num:");
    scanf("%d",&m);
    for(i=2;i<=m;i++)
    {
        while(m!=i)
        {
            if(m%i==0)
            {printf("%d*",i);
           m=m/i;
            }
                else
                    break;
        }
    }
    printf("%d\n",m);
    */
    static int k[10];
    int i,j,n,s;
    for(j=2;j<1000;j++)
    {
        n=-1;s=j;
        for(i=1;i<j;i++)
        {
            if((j%i)==0)
            {
                n++;
                s=s-i;
                k[n]=i;
            }
        }
        if(s==0)
        {
            printf("%d is a wanshu",j);
            for(i=0;i<n;i++)
       printf("%d,",k[i]);
            printf("%d\n",k[n]);
        }
    }
}
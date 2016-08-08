#include<stdio.h>
int main()
{
  /*  int i,m,n;
    printf("enter two number:\n");
    scanf("%d%d",&m,&n);
    while(i<=m&&i<=n)
        {if((m%i==0)&&(n%i==0))
         printf("%d\n",i);
        }
    while(i>=m&&i>=n)
        {if(i%m==0&&i%n==0)
            printf("m*i=%d\n",m*i);
            else break;
        }
        */
    int a,b,m,n,t;
    printf("please input two numbers:");
    scanf("%d,%d",&m,&n);
    if(m<n)
    {
        t=m;
        m=n;
        n=t;
    }
    a=m;b=n;
    while(b!=0)
    { t=a%b;a=b;b=t;
    }
    printf("gongyueshu:%d\n",a);
    printf("gongbeishu:%d\n",m*n/a);
}



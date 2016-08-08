#include<stdio.h>
int main()
{
    int i,t,n=20;
 float a=2,b=1,s=0;
    for(i=1;i<=n;i++) 
    {
        s=s+a/b;
        t=a;
        a=a+b;
        b=t;
    }
    printf("%f\n",s);
}

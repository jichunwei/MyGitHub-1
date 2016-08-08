#include<stdio.h>
int main()
{
    float power(float n,int p);
    int b;
    float a,c;

    printf("please input two nums(enter q to quit):");
    while(scanf("%1f%d",&a,&b)==2)
    {
        c=power(a,b);
        printf("%.3f to the power %d is %0.5f\n",a,b,c);
    }
    printf("bye!\n");
    return 0;
}
float power(float n,int p)
{
    float m=1;
    int i;
    
    if(p>0)
    {
        for(i=1;i<=p;i++)
            m*=n;
    }
    if(p<0)
    {
    for(i=1;i<=-p;i++)
       m*=n;
    m=1/m;
    }
    
    if(n=0)  m=0;
    if(p=0)  m=1;
    return m;
}



       



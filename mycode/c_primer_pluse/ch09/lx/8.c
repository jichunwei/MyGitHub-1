#include<stdio.h>
float power(float n,int p);
int main()
{
    int b;
    float a,c;

    printf("please input two nums(enter q to quit):\n");
    while(scanf("%1f %d",&a,&b)==2)
    {
        c=power(a,b);
        printf("a=%.3f b=%d c=%d\n",a,b,c);
    }
        printf("\n");
        return 0;
}
float power(float n,int p)
{
    float m=1;
    int i;
    
    if(n=0) m=0;
    while(n>0)
    {
        if(-p>0)
          m*=n;
         else
         m=1;
    }
    m=1/m;
    return m;
}
    




        

    

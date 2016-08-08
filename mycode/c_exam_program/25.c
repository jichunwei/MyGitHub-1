#include<stdio.h>
int main()
{
    float i,s=0,t=1;
    for(i=1;i<=20;i++)
    {
        t*=i;
        s+=t;
    }
    printf("1+2!+3!+.....+20!)=%e\n",s);
}
            
